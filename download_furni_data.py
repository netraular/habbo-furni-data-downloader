# dependencies/habbo-furni-data-downloader/download_furni_data.py

import requests
import json
import time
from pathlib import Path

# --- LIST OF HOTELS (se mantiene para ser importada) ---
HOTELS = [
    {"id": 1, "name": "Habbo.com", "short_name": "COM"},
    {"id": 2, "name": "Habbo Brazil", "short_name": "COM.BR"},
    {"id": 3, "name": "Habbo Spain", "short_name": "ES"},
    {"id": 4, "name": "Habbo Finland", "short_name": "FI"},
    {"id": 5, "name": "Habbo France", "short_name": "FR"},
    {"id": 6, "name": "Habbo Germany", "short_name": "DE"},
    {"id": 7, "name": "Habbo Italy", "short_name": "IT"},
    {"id": 8, "name": "Habbo Netherlands", "short_name": "NL"},
    {"id": 9, "name": "Habbo Turkey", "short_name": "COM.TR"},
    {"id": 10, "name": "Habbo Sandbox", "short_name": "Sandbox"},
]

def download_furni_by_hotel(hotel, api_token: str, output_dir: Path):
    """
    Downloads all furni data for a specific hotel, handling pagination.
    """
    BASE_URL = "https://habbofurni.com/api/v1"
    HEADERS = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }

    hotel_id = hotel["id"]
    hotel_name = hotel["name"]
    print(f"\n--- Starting download for hotel: {hotel_name} (ID: {hotel_id}) ---")

    hotel_headers = HEADERS.copy()
    hotel_headers["X-Hotel-ID"] = str(hotel_id)

    all_furni_data = []
    
    try:
        print("Fetching pagination info...")
        params = {"per_page": 100, "page": 1}
        response = requests.get(f"{BASE_URL}/furniture", headers=hotel_headers, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        total_pages = data["meta"]["last_page"]
        total_furni = data["meta"]["total"]
        
        print(f"Hotel '{hotel_name}' has {total_furni} furni across {total_pages} pages.")
        all_furni_data.extend(data["data"])
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error on initial request for hotel {hotel_name}: {e}")
        return False

    for page in range(2, total_pages + 1):
        try:
            print(f"Downloading page {page} of {total_pages}...")
            params["page"] = page
            response = requests.get(f"{BASE_URL}/furniture", headers=hotel_headers, params=params, timeout=15)
            response.raise_for_status()
            page_data = response.json()["data"]
            all_furni_data.extend(page_data)
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error downloading page {page} for {hotel_name}: {e}. Skipping page.")
            continue
            
    if all_furni_data:
        file_name = f"{hotel['short_name'].replace('.', '_')}_furnis.json"
        file_path = output_dir / file_name
        
        print(f"Saving {len(all_furni_data)} furni to file: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_furni_data, f, indent=2, ensure_ascii=False)
        print(f"✔️ Download complete for {hotel_name}!")
    
    return True