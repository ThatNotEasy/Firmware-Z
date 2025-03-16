from modules.vestel import firmware_vestel, vestel_extractor
from modules.samsung import samsung_firmware, samsung_extractor
from modules.banners import banners
from colorama import Fore, Style, init
import time

init()

def display_brand_menu():
    print(Fore.CYAN + "╔══════════════════════════════════════════════════╗")
    print(Fore.CYAN + "║" + Fore.YELLOW + "                   CHOOSE A BRAND                 " + Fore.CYAN + "║")
    print(Fore.CYAN + "╠══════════════════════════════════════════════════╣")
    print(Fore.CYAN + "║" + Fore.RED + " 1. " + Fore.YELLOW + "SAMSUNG                                       " + Fore.CYAN + "║")
    print(Fore.CYAN + "║" + Fore.RED + " 2. " + Fore.YELLOW + "TOSHIBA                                       " + Fore.CYAN + "║")
    print(Fore.CYAN + "╚══════════════════════════════════════════════════╝" + Fore.RESET)
    print()

def get_user_choice():
    while True:
        choice = input(Fore.WHITE + "ROOT@FIRMWARE-Z: " + Fore.RED)
        if choice in ["1", "2"]:
            return choice
        else:
            print(Fore.RED + "INVALID CHOICE. PLEASE ENTER 1 OR 2." + Fore.RESET)
            time.sleep(1)

def handle_samsung():
    """HANDLE SAMSUNG FIRMWARE EXTRACTION."""
    response = samsung_firmware()
    if response and samsung_extractor(response):
        return True
    else:
        print(Fore.RED + "NO FIRMWARE FOUND FOR THE PROVIDED CODE. PLEASE TRY ANOTHER CODE." + Fore.RESET)
        time.sleep(2)
        return False

def handle_toshiba():
    """HANDLE TOSHIBA FIRMWARE EXTRACTION."""
    code = input(f"{Fore.WHITE}ENTER YOUR MODEL CODE {Fore.RED}(EXAMPLE: MB130): {Fore.RESET}")
    current_page = 1
    while current_page <= 37:
        response = firmware_vestel(code, current_page)
        if response:
            exit_program, current_page = vestel_extractor(response, current_page)
            if exit_program:
                break
        else:
            print(Fore.RED + "FAILED TO FETCH DATA. EXITING..." + Fore.RESET)
            break
    return True

if __name__ == "__main__":
    while True:
        banners()
        display_brand_menu()
        choice = get_user_choice()
        if choice == "1":
            banners()
            if handle_samsung():
                break
        elif choice == "2":
            banners()
            if handle_toshiba():
                break