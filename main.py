from modules.vestel import firmware_vestel
from modules.extractor import vestel_extractor
from modules.banners import banners
from colorama import Fore
import time

if __name__ == "__main__":
    while True:
        banners()
        code = input(f"Enter the code {Fore.RED}(Example: MB130): {Fore.RESET}")
        response = firmware_vestel(code)
        if response and vestel_extractor(response):
            break
        else:
            print(Fore.RED + "No content found for the provided code. Please try another code." + Fore.RESET)
            time.sleep(2)