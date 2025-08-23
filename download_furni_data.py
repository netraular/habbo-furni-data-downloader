# download_furni.py

import requests
import json
import time
import os
from config import API_TOKEN # Import the token from the new config file

# --- CONFIGURATION ---
BASE_URL = "https://habbofurni.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}
OUTPUT_DIR = "habbo_furni_data"

# --- LIST OF HOTELS (from the API documentation) ---
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

def download_furni_by_hotel(hotel):
    """
    Downloads all furni data for a specific hotel, handling pagination.
    """
    hotel_id = hotel["id"]
    hotel_name = hotel["name"]
    print(f"\n--- Starting download for hotel: {hotel_name} (ID: {hotel_id}) ---")

    hotel_headers = HEADERS.copy()
    hotel_headers["X-Hotel-ID"] = str(hotel_id)

    all_furni_data = []
    
    try:
        print("Fetching pagination info...")
        params = {"per_page": 100, "page": 1}
        response = requests.get(f"{BASE_URL}/furniture", headers=hotel_headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        total_pages = data["meta"]["last_page"]
        total_furni = data["meta"]["total"]
        
        print(f"Hotel '{hotel_name}' has {total_furni} furni across {total_pages} pages.")
        all_furni_data.extend(data["data"])
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error on initial request for hotel {hotel_name}: {e}")
        return

    # Loop through the rest of the pages
    for page in range(2, total_pages + 1):
        try:
            print(f"Downloading page {page} of {total_pages}...")
            params["page"] = page
            response = requests.get(f"{BASE_URL}/furniture", headers=hotel_headers, params=params)
            response.raise_for_status()
            page_data = response.json()["data"]
            all_furni_data.extend(page_data)
            time.sleep(0.5) # Be polite to the API, wait half a second between requests
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error downloading page {page} for {hotel_name}: {e}. Skipping page.")
            continue
            
    # Save all the collected data to a JSON file
    if all_furni_data:
        file_name = f"{hotel['short_name'].replace('.', '_')}_furnis.json"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        
        print(f"Saving {len(all_furni_data)} furni to file: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_furni_data, f, indent=2, ensure_ascii=False)
        print(f"✔️ Download complete for {hotel_name}!")

def show_menu():
    """Displays the interactive menu and handles user selection."""
    while True:
        print("\n" + "="*50)
        print("    Select which hotel you want to download data for")
        print("="*50)
        for i, hotel in enumerate(HOTELS):
            print(f" [{i+1}] {hotel['name']}")
        print("----------------------------------------------------")
        print(" [0] Download data for ALL hotels")
        print(" [Q] Quit")
        print("="*50)

        choice = input("Enter your choice and press Enter: ").strip().lower()

        if choice == 'q':
            print("Exiting the program. Goodbye!")
            break
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                print("You have selected to download ALL hotels. This may take a while...")
                for hotel in HOTELS:
                    download_furni_by_hotel(hotel)
                print("\n🎉 Process completed for all hotels.")
            elif 1 <= choice_num <= len(HOTELS):
                selected_hotel = HOTELS[choice_num - 1]
                download_furni_by_hotel(selected_hotel)
            else:
                print("❌ Invalid option. Please choose a number from the list.")
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'Q' to quit.")

if __name__ == "__main__":
    # Check if the API token is configured before running
    if not API_TOKEN or API_TOKEN == "YOUR_BEARER_TOKEN_HERE":
        print("❌ ERROR: API_TOKEN is not configured in 'config.py'.")
        print("Please edit 'config.py' and add your token before running the script.")
    else:
        # Create the output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        show_menu()