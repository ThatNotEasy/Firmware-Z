from modules.vestel import firmware_vestel
from modules.banners import banners
from colorama import Fore

if __name__ == "__main__":
    banners()
    code = input(f"Enter the code {Fore.RED}(Example: MB130): {Fore.RESET}")
    firmware_vestel(code)