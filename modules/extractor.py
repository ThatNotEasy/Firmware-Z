from bs4 import BeautifulSoup
from colorama import Fore, Style, init
import os, time, sys, requests, re, urllib3

init()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_code_info(url):
    filename = url.split("/")[-1].split(".")[0]
    parts = filename.split("_")
    parsed_info = {
        "FIRMWARE CODE": parts[0] if parts else "N/A",
        "MODEL CODE": parts[1] if len(parts) > 1 else "N/A",
        "BRAND NAME": parts[2] if len(parts) > 2 else "N/A",
        "VERSION NUMBER": parts[-2] if len(parts) > 5 else "N/A",
        "SERIES": "_".join(parts[4:-2]) if len(parts) > 4 else "N/A"
    }
    if parsed_info["BRAND NAME"] == "TOS":
        parsed_info["BRAND NAME"] = "TOSHIBA"
    if not parsed_info["SERIES"].startswith("QUI_"):
        parsed_info["SERIES"] = "QUI_" + parsed_info["SERIES"]
    return parsed_info

# ============================================================================================================= #

def modify_download_url(url):
    return url.replace(
        "http://www.vestel-spares.co.uk/",
        "https://portal.repairtech.co.uk/downloads/"
    ).split('?')[0]

# ============================================================================================================= #

def print_header(title, width=70):
    print(Fore.CYAN + "╔" + "═" * width + "╗")
    print(Fore.CYAN + "║" + Fore.YELLOW + f" {title.center(width - 2)}" + Fore.CYAN + " ║")
    print(Fore.CYAN + "╠" + "═" * width + "╣")

# ============================================================================================================= #

def print_footer(width=70):
    print(Fore.CYAN + "╚" + "═" * width + "╝")

# ============================================================================================================= #

def print_key_value(key, value, width=70, key_color=Fore.BLUE, value_color=Fore.MAGENTA):
    if isinstance(value, list):
        value = ", ".join(map(str, value))

    print(Fore.CYAN + "║" + key_color + f" {key.ljust(20)}" + Fore.CYAN + "- " + value_color + f"{value.ljust(width - 26)}" + Fore.CYAN + "   ║")


# ============================================================================================================= #

def print_url(url, width=70):
    url_label = " Download URL"
    available_space = width - 24
    print(Fore.CYAN + "║" + Fore.GREEN + f"{url_label.ljust(20)}" + Fore.CYAN + ": " + Fore.WHITE + f"{url[:available_space]}" + Fore.CYAN + "  ║")
    if len(url) > available_space:
        for i in range(available_space, len(url), available_space):
            chunk = url[i:i + available_space]
            print(Fore.CYAN + "║" + " " * 22 + Fore.WHITE + f"{chunk.ljust(available_space)}" + Fore.CYAN + "  ║")

# ============================================================================================================= #

def print_parsed_info(parsed_info, download_url, width=70):
    print_header("Firmware Information", width)
    for key, value in parsed_info.items():
        if key != "Mirrors" and key != "Download URL":
            print_key_value(key, value, width, key_color=Fore.BLUE, value_color=Fore.MAGENTA)
    
    # Print the download URL
    print(Fore.CYAN + "╠" + "═" * width + "╣")
    print_url(download_url, width)
    print_footer(width)

# ============================================================================================================= #

def loading_animation(message):
    chars = "/—\\|"
    for _ in range(10):
        for char in chars:
            sys.stdout.write(f"\r{Fore.CYAN}{message} {char}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
            
# ============================================================================================================= #

def download_file(url, filename):
    try:
        os.makedirs("output", exist_ok=True)
        file_path = os.path.join("output", filename)

        with requests.get(url, stream=True, verify=False) as response:
            response.raise_for_status()

            content_disp = response.headers.get("Content-Disposition", "")
            if "filename=" in content_disp:
                filename = content_disp.split("filename=")[1].strip("\"")
                file_path = os.path.join("output", filename)

            print(f"{Fore.YELLOW}[*] {Fore.WHITE}DOWNLOADING FILE AS: {Fore.GREEN}{filename}{Fore.RESET}")
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100 if total_size else 0
                        print(f"\r{Fore.YELLOW}[*] {Fore.WHITE}DOWNLOADED: {Fore.GREEN}{downloaded}/{total_size} {Fore.WHITE}BYTES {Fore.GREEN}({percent:.2f}%){Fore.RESET}", end="")

            print(f"\n{Fore.YELLOW}[*] {Fore.GREEN}FILE SUCCESSFULLY DOWNLOADED{Fore.RESET}\n")
            return file_path

    except Exception as e:
        print(Fore.RED + f"❌ ERROR: {str(e)}" + Style.RESET_ALL)
        return None
    
# ============================================================================================================= #

def extract_firmware_links(html):
    """Extracts firmware links from the HTML table."""
    soup = BeautifulSoup(html, 'html.parser')
    firmware_list = []
    table_rows = soup.select("tbody tr")
    for row in table_rows:
        columns = row.find_all("td")
        if len(columns) == 2:
            model_name = columns[0].text.strip()
            link_element = columns[1].find("a")
            if link_element and "href" in link_element.attrs:
                download_link = link_element["href"]
                firmware_list.append({"Model Name": model_name, "Download Link": download_link})
    return firmware_list

# ============================================================================================================= #

def extract_text(article_block, label):
    label_element = article_block.find(string=label)
    if label_element:
        next_element = label_element.find_next(string=True)
        return next_element.strip() if next_element else "Not Available"
    return "Not Available"

# ============================================================================================================= #

def extract_firmware_details(firmware_url):
    """Extracts firmware details and returns them directly (not as a dictionary)."""
    response = requests.get(firmware_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_block = soup.find("div", {"id": "article-block"})
        if article_block:
            file_name = extract_text(article_block, "File Name")
            country = extract_text(article_block, "Country")
            file_size = extract_text(article_block, "File Size")
            android_version = extract_text(article_block, "Android Version")
            mirrors = extract_mirror_links(article_block)
            return file_name, country, file_size, android_version, mirrors
    return None


# ============================================================================================================= #

def extract_mirror_links(article_block):
    """Extracts the first valid mirror link, prioritizing Google Drive over Mediafire."""
    for link in article_block.find_all("a", href=True):
        link_url = link["href"]
        if "drive.google.com" in link_url:
            return link_url  # Return Google Drive link immediately
        elif "mediafire.com" in link_url:
            return link_url  # Return Mediafire link if no Google Drive link is found
    return None  # Return None if no valid mirror links are found

# ============================================================================================================= #

def extract_google_drive_id(drive_url):
    """Extracts the file ID from a Google Drive URL."""
    patterns = [
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",  # Format: file/d/{id}
        r"id=([a-zA-Z0-9_-]+)"  # Format: ?id={id}
    ]
    
    for pattern in patterns:
        match = re.search(pattern, drive_url)
        if match:
            return match.group(1)
    
    return None  # Return None if no match

# ============================================================================================================= #

def sanitize_filename(filename):
    """Removes invalid characters from filenames for Windows and Linux."""
    return re.sub(r'[\/:*?"<>|]', '_', filename)

# ============================================================================================================= #

def download_from_google_drive(drive_url, filename):
    """Downloads a file from Google Drive and saves it in the output folder."""
    file_id = extract_google_drive_id(drive_url)
    
    if not file_id:
        print(Fore.RED + "❌ FAILED TO EXTRACT GOOGLE DRIVE FILE ID." + Style.RESET_ALL)
        return
    
    os.makedirs("output", exist_ok=True)
    
    # Sanitize filename before saving
    sanitized_filename = sanitize_filename(filename)
    file_path = os.path.join("output", sanitized_filename)

    with requests.get(f'https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm=t', stream=True, verify=False) as response:
        response.raise_for_status()
        content_disp = response.headers.get("Content-Disposition", "")
        if "filename=" in content_disp:
            filename = content_disp.split("filename=")[1].strip("\"")
            filename = sanitize_filename(filename)  # Sanitize it again
            file_path = os.path.join("output", filename)

        print(f"[*] DOWNLOADING FILE AS: {filename}")
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = (downloaded / total_size) * 100 if total_size else 0
                    print(f"\r[*] DOWNLOADED: {downloaded}/{total_size} BYTES ({percent:.2f}%)", end="")

        print(f"\n[*] FILE SUCCESSFULLY DOWNLOADED: {file_path}")
    sys.exit()