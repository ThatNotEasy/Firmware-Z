import requests
from modules.extractor import vestel_extractor

def firmware_vestel(code):
    try:
        code = str(code)  # Pastikan kode adalah angka
    except ValueError:
        print("Invalid input. Please enter a valid code.")
        return

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
        response = requests.get(f'https://www.vestel-spares.co.uk/index.php?route=product/search&search={code}', cookies=cookies, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to fetch data - {e}")
        return

    if response.status_code == 200:
        vestel_extractor(response.text)
    else:
        print(f"Error: Received status code {response.status_code}")