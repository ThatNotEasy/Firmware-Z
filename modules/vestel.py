import requests, gzip, zipfile, os, shutil
from modules.banners import banners
from modules.extractor import loading_animation, parse_code_info, print_parsed_info, modify_download_url, download_file
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

def firmware_vestel(model, page=1):
    try:
        model = str(model)
    except ValueError:
        print("Invalid input. Please enter a valid model code.")
        return None

    cookies = {
        'language': 'en',
        'currency': 'GBP',
        'PHPSESSID': '7757cdc6bdd190a6ea89be7daf4002e7',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ms;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.vestel-spares.co.uk/index.php?route=common/home',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(
            f'https://www.vestel-spares.co.uk/index.php?route=product/search&search={model}&page={page}',
            cookies=cookies,
            headers=headers
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to fetch data - {e}")
        return None

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error: Received status code {response.status_code}")
        return None
    
# ===================================================================================================================================== #

def vestel_extractor(response, current_page):
    soup = BeautifulSoup(response, 'html.parser')
    products = soup.find_all('div', class_='product-layout')
    
    if not products:
        print(Fore.RED + "\nNO PRODUCTS FOUND FOR THE PROVIDED CODE." + Fore.RESET)
        return False, current_page
    
    for idx, product in enumerate(products, start=1):
        product_url = product.find('div', class_='image').find('a')['href']
        product_description = product.find('div', class_='caption').find('p').text.strip()
        modified_download_url = modify_download_url(product_url)
        parsed_info = parse_code_info(modified_download_url)
        parsed_info["FIRMWARE CODE"] = product_description.split()[0] if product_description else "N/A"
        print(Fore.YELLOW + f"\n[{idx}]:")
        print_parsed_info(parsed_info, modified_download_url)
    
    print(f"\n{Fore.RED}FOOTPRINTS NOTES: {Fore.WHITE}PRESS {Fore.GREEN}N/P{Fore.WHITE} TO GO {Fore.GREEN}NEXT/PREVIOUS {Fore.WHITE}PAGE. {Fore.RED}Q{Fore.WHITE} TO EXIT.{Fore.RESET}")
    print(Fore.CYAN + "═" * 17)
    
    choice = input(Fore.WHITE + "\nROOT@FIRMWARE-Z: " + Fore.RED).strip().upper()
    
    if choice.isdigit():
        selection = int(choice) - 1
        if 0 <= selection < len(products):
            selected_product = products[selection]
            selected_url = modify_download_url(selected_product.find('div', class_='image').find('a')['href'])
            filename = selected_url.split("/")[-1]
            banners()
            download_file(selected_url, filename)
            
            zip_path = os.path.join("output", filename)
            if zipfile.is_zipfile(zip_path):
                loading_animation(f"{Fore.YELLOW}[*] {Fore.WHITE}UNZIPPING{Fore.RESET}")
                print(f"\n{Fore.YELLOW}[*] {Fore.GREEN}UNZIPPED{Fore.RESET}\n")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall("output")
                
                loading_animation(f"{Fore.YELLOW}[*] {Fore.GREEN}REMOVING{Fore.RESET}")
                os.remove(zip_path)
                print(f"\n{Fore.YELLOW}[*] {Fore.GREEN}REMOVED{Fore.RESET}\n")
            else:
                print(Fore.RED + f"{filename} IS NOT A VALID ZIP FILE. SKIPPING UNZIP." + Style.RESET_ALL)
            
            for root, dirs, files in os.walk("output"):
                for file in files:
                    if file.endswith(".gz"):
                        gz_path = os.path.join(root, file)
                        output_file = gz_path[:-3]
                        loading_animation(f"{Fore.YELLOW}[*] {Fore.GREEN}EXTRACTING{Fore.RESET}")
                        try:
                            with gzip.open(gz_path, 'rb') as gz_file:
                                with open(output_file, 'wb') as out_file:
                                    shutil.copyfileobj(gz_file, out_file)
                            print(f"{Fore.YELLOW}[*] {Fore.GREEN}EXTRACTED{Fore.RESET}\n")
                            
                            loading_animation(f"{Fore.YELLOW}[*] {Fore.GREEN}REMOVING{Fore.RESET}")
                            os.remove(gz_path)
                            print(f"{Fore.YELLOW}[*] {Fore.GREEN}REMOVED{Fore.RESET}\n")
                        except Exception as e:
                            print(Fore.RED + f"FAILED TO EXTRACT {file}: {e}" + Style.RESET_ALL)
            
            print(Fore.GREEN + f"DOWNLOAD AND EXTRACTION COMPLETED{Fore.RESET}\n")
            return True, current_page
        else:
            print(Fore.RED + "INVALID SELECTION." + Fore.RESET)
            return False, current_page
    elif choice == "N":
        return False, current_page + 1
    elif choice == "P":
        return False, max(1, current_page - 1)
    elif choice == "Q":
        return True, current_page
    else:
        print(Fore.RED + "INVALID CHOICE. PLEASE TRY AGAIN." + Fore.RESET)
        return False, current_page