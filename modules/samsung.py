import requests, gzip, zipfile, os, shutil, sys
from modules.banners import banners
from modules.extractor import extract_firmware_links, extract_firmware_details, download_from_google_drive, print_parsed_info, extract_mirror_links
from prettytable import PrettyTable
from colorama import Fore, Style, init

def samsung_firmware():
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        response = requests.get('https://androidmtk.com/download-samsung-stock-rom', headers=headers)
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

def display_firmware_page(firmware_data, page, per_page=10):
    """
    Displays a paginated list of firmware models with numbers and model names in different colors.
    
    Args:
        firmware_data (list): List of firmware data containing model names.
        page (int): Current page number.
        per_page (int): Number of items to display per page. Default is 10.
    """
    start = page * per_page
    end = start + per_page
    paginated_data = firmware_data[start:end]

    col_width_no = 5
    col_width_model = 40

    total_width = (col_width_no + col_width_model + col_width_no + col_width_model + 11)  # Increased by 2 to fix missing ═

    header = f"║ {'NO'.center(col_width_no)} ║ {'CHOOSE A MODEL'.center(col_width_model)} ║ {'NO'.center(col_width_no)} ║ {'CHOOSE A MODEL'.center(col_width_model)} ║"
    separator = "╠" + "═" * (col_width_no + 2) + "╬" + "═" * (col_width_model + 2) + "╬" + "═" * (col_width_no + 2) + "╬" + "═" * (col_width_model + 2) + "╣"

    print(Fore.CYAN + "╔" + "═" * total_width + "╗")
    print(Fore.CYAN + header)
    print(Fore.CYAN + separator)

    for i in range(0, len(paginated_data), 2):
        left = paginated_data[i]
        left_idx = str(start + i + 1).rjust(col_width_no)
        left_model = left['Model Name'].ljust(col_width_model)

        if i + 1 < len(paginated_data):
            right = paginated_data[i + 1]
            right_idx = str(start + i + 2).rjust(col_width_no)
            right_model = right['Model Name'].ljust(col_width_model)
        else:
            right_idx = " ".rjust(col_width_no)
            right_model = " ".ljust(col_width_model)

        # Apply different colors to numbers and model names
        print(Fore.CYAN + f"║ {Fore.YELLOW}{left_idx}{Fore.CYAN} ║ {Fore.GREEN}{left_model}{Fore.CYAN} ║ {Fore.YELLOW}{right_idx}{Fore.CYAN} ║ {Fore.GREEN}{right_model}{Fore.CYAN} ║")

    print(Fore.CYAN + "╚" + "═" * total_width + "╝" + Fore.RESET)


def samsung_extractor(response):
    firmware_data = extract_firmware_links(response)
    page = 0
    per_page = 10

    while True:
        display_firmware_page(firmware_data, page, per_page)

        try:
            # Display user instructions
            print(f"\n{Fore.RED}FOOTPRINTS NOTES: {Fore.WHITE}PRESS {Fore.GREEN}N/P{Fore.WHITE} TO GO {Fore.GREEN}NEXT/PREVIOUS {Fore.WHITE}PAGE. {Fore.RED}Q{Fore.WHITE} TO EXIT.{Style.RESET_ALL}")
            print(Fore.CYAN + "═" * 17)

            # Get user input
            choice = input(Fore.WHITE + "\nROOT@FIRMWARE-Z: " + Fore.RED).strip().upper()

            # Handle user choice
            if choice == "Q":
                print("\nEXITING...".upper())
                sys.exit()

            elif choice == "N":
                if (page + 1) * per_page < len(firmware_data):
                    page += 1
                else:
                    print(Fore.YELLOW + "\nYOU ARE ALREADY ON THE LAST PAGE.".upper() + Style.RESET_ALL)

            elif choice == "P":
                if page > 0:
                    page -= 1
                else:
                    print(Fore.YELLOW + "\nYOU ARE ALREADY ON THE FIRST PAGE.".upper() + Style.RESET_ALL)

            elif choice.isdigit():
                choice = int(choice) - 1  # Convert to zero-based index
                if 0 <= choice < len(firmware_data):
                    selected_firmware = firmware_data[choice]
                    banners()
                    print(f"\n{Fore.WHITE}FETCHING DETAILS FOR: {Fore.GREEN}{selected_firmware['Model Name']}{Fore.RESET}\n".upper())

                    firmware_details = extract_firmware_details(selected_firmware["Download Link"])

                    if firmware_details:
                        # Unpack the tuple returned by extract_firmware_details
                        file_name, country, file_size, android_version, mirrors = firmware_details
                        parsed_info = {
                            "File Name": file_name,
                            "Country": country,
                            "File Size": file_size,
                            "Android Version": android_version,
                            "Mirrors": mirrors
                        }
                        
                        download_url = mirrors  # extract_mirror_links already returns a single URL or None
                        print_parsed_info(parsed_info, download_url)

                        if download_url:
                            if "drive.google.com" in download_url:
                                # print(Fore.GREEN + "\nGOOGLE DRIVE LINK FOUND. DOWNLOADING...".upper() + Style.RESET_ALL)
                                download_from_google_drive(download_url, file_name)
                            elif "mediafire.com" in download_url:
                                print(Fore.YELLOW + "\nMEDIAFIRE LINK FOUND. PLEASE DOWNLOAD MANUALLY.".upper() + Style.RESET_ALL)
                            else:
                                print(Fore.YELLOW + "\nUNKNOWN MIRROR LINK. PLEASE DOWNLOAD MANUALLY.".upper() + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "\nNO VALID MIRROR LINK FOUND. PLEASE DOWNLOAD MANUALLY.".upper() + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "\nFAILED TO EXTRACT FIRMWARE DETAILS.".upper() + Style.RESET_ALL)
                else:
                    print(Fore.RED + "\nINVALID SELECTION. PLEASE CHOOSE A VALID NUMBER.".upper() + Style.RESET_ALL)

            else:
                print(Fore.RED + "\nINVALID INPUT. PLEASE ENTER A VALID NUMBER OR COMMAND.".upper() + Style.RESET_ALL)

        except ValueError:
            print(Fore.RED + "\nINVALID INPUT. PLEASE ENTER A VALID NUMBER.".upper() + Style.RESET_ALL)