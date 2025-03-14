from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from tqdm import tqdm
from modules.banners import banners
import textwrap, os, time, sys, requests, zipfile, shutil, gzip

init()

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

def print_gradient_text(text, width=70):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    gradient_text = ""
    for i, char in enumerate(text):
        gradient_text += colors[i % len(colors)] + char
    print(gradient_text.center(width))

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
    print(Fore.CYAN + "║" + key_color + f" {key.ljust(20)}" + Fore.CYAN + ": " + value_color + f"{value.ljust(width - 26)}" + Fore.CYAN + "   ║")

# ============================================================================================================= #

def print_url(url, width=70):
    url_label = " Download URL"
    print(Fore.CYAN + "║" + Fore.GREEN + f"{url_label.ljust(20)}" + Fore.CYAN + ": " + Fore.WHITE + f"{url[:width - 24]}" + Fore.CYAN + "  ║")
    wrapped_url = textwrap.wrap(url, width=width - 24)
    for line in wrapped_url[1:]:
        print(Fore.CYAN + "║" + " " * 22 + Fore.WHITE + f"{line.ljust(width - 24)}" + Fore.CYAN + "  ║")

# ============================================================================================================= #

def print_parsed_info(parsed_info, download_url, width=70):
    print_header("Firmware Information", width)
    for key, value in parsed_info.items():
        print_key_value(key, value, width)
    print(Fore.CYAN + "╠" + "═" * width + "╣")
    print_url(download_url, width)
    print_footer(width)

# ============================================================================================================= #

def download_file(url, filename):
    if not os.path.exists("output"):
        os.makedirs("output")
    
    file_path = os.path.join("output", filename)
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(file_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

# ============================================================================================================= #

def vestel_extractor(response):
    soup = BeautifulSoup(response, 'html.parser')
    products = soup.find_all('div', class_='product-layout')
    for idx, product in enumerate(products, start=1):
        product_url = product.find('div', class_='image').find('a')['href']
        product_description = product.find('div', class_='caption').find('p').text.strip()
        modified_download_url = modify_download_url(product_url)
        parsed_info = parse_code_info(modified_download_url)
        parsed_info["FIRMWARE CODE"] = product_description.split()[0] if product_description else "N/A"
        print(Fore.YELLOW + f"\nProduct {idx}:")
        print_parsed_info(parsed_info, modified_download_url)
    
    selection = int(input(Fore.GREEN + "\nEnter the number of the product you want to download: ")) - 1
    if 0 <= selection < len(products):
        selected_product = products[selection]
        selected_url = modify_download_url(selected_product.find('div', class_='image').find('a')['href'])
        filename = selected_url.split("/")[-1]
        banners()
        print(Fore.GREEN + f"Downloading: {Fore.RED}{filename}{Fore.RESET}\n")
        download_file(selected_url, filename)
        
        zip_path = os.path.join("output", filename)
        if zipfile.is_zipfile(zip_path):
            print(Fore.CYAN + f"\nUnzipping {filename}..." + Style.RESET_ALL)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("output")
            print(Fore.GREEN + f"Unzipping completed: {filename}" + Style.RESET_ALL)
            
            os.remove(zip_path)
            print(Fore.RED + f"Removed: {filename}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"{filename} is not a valid ZIP file. Skipping unzip." + Style.RESET_ALL)
        
        for root, dirs, files in os.walk("output"):
            for file in files:
                if file.endswith(".gz"):
                    gz_path = os.path.join(root, file)
                    output_file = gz_path[:-3]
                    print(Fore.CYAN + f"\nExtracting {file}..." + Style.RESET_ALL)
                    try:
                        with gzip.open(gz_path, 'rb') as gz_file:
                            with open(output_file, 'wb') as out_file:
                                shutil.copyfileobj(gz_file, out_file)
                        print(Fore.GREEN + f"Extraction completed: {file}" + Style.RESET_ALL)
                        
                        os.remove(gz_path)
                        print(Fore.RED + f"Removed: {file}" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Failed to extract {file}: {e}" + Style.RESET_ALL)
        
        print(Fore.GREEN + f"Download and extraction completed: {Fore.RED}{filename}{Fore.RESET}")
    else:
        print(Fore.RED + "Invalid selection.")