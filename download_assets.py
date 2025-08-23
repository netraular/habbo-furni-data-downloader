# download_assets.py

import os
import json
import requests
import time

# --- CONFIGURATION ---
# The directory where process_furni.py saved its output
BASE_DIR = "furni_database"
# Be polite to the server, wait a small amount of time between downloads
DOWNLOAD_DELAY_SECONDS = 0.2

def download_all_assets():
    """
    Iterates through all the furni folders in the base directory,
    reads their data.json, and downloads the associated SWF and icon files.
    """
    print("Starting asset download script...")
    
    if not os.path.exists(BASE_DIR):
        print(f"❌ ERROR: The directory '{BASE_DIR}' was not found.")
        print("Please run process_furni.py first to generate the database structure.")
        return

    # Get a list of all furni folders
    try:
        furni_folders = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
        total_furni = len(furni_folders)
        print(f"Found {total_furni} furni folders to process.\n")
    except FileNotFoundError:
        print(f"❌ ERROR: The directory '{BASE_DIR}' seems to be empty or missing.")
        return

    # Counters for the final summary
    downloaded_swfs = 0
    downloaded_icons = 0
    skipped_files = 0
    error_count = 0

    # Process each folder
    for i, folder_name in enumerate(furni_folders):
        furni_folder_path = os.path.join(BASE_DIR, folder_name)
        data_json_path = os.path.join(furni_folder_path, "data.json")

        print(f"[{i+1}/{total_furni}] Processing '{folder_name}'...")

        if not os.path.exists(data_json_path):
            print(f"  ⚠️ Warning: 'data.json' not found in this folder. Skipping.")
            continue

        try:
            with open(data_json_path, 'r', encoding='utf-8') as f:
                furni_data = json.load(f)

            # --- Download SWF ---
            swf_info = furni_data.get("hotelData", {}).get("swf", {})
            if swf_info.get("exists") and swf_info.get("url"):
                file_url = swf_info["url"]
                file_name = os.path.basename(file_url) # Extracts "fireplace_armas.swf"
                output_path = os.path.join(furni_folder_path, file_name)

                if not os.path.exists(output_path):
                    try:
                        response = requests.get(file_url, timeout=10)
                        response.raise_for_status()
                        with open(output_path, 'wb') as out_file:
                            out_file.write(response.content)
                        print(f"  ✔️ Downloaded SWF: {file_name}")
                        downloaded_swfs += 1
                        time.sleep(DOWNLOAD_DELAY_SECONDS) # Wait after a successful download
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ Error downloading SWF {file_url}: {e}")
                        error_count += 1
                else:
                    print(f"  ⏩ SWF already exists. Skipping.")
                    skipped_files += 1
            
            # --- Download Icon (Bonus) ---
            icon_info = furni_data.get("hotelData", {}).get("icon", {})
            if icon_info.get("exists") and icon_info.get("url"):
                file_url = icon_info["url"]
                file_name = os.path.basename(file_url) # Extracts "fireplace_armas_icon.png"
                output_path = os.path.join(furni_folder_path, file_name)

                if not os.path.exists(output_path):
                    try:
                        response = requests.get(file_url, timeout=10)
                        response.raise_for_status()
                        with open(output_path, 'wb') as out_file:
                            out_file.write(response.content)
                        print(f"  ✔️ Downloaded Icon: {file_name}")
                        downloaded_icons += 1
                        time.sleep(DOWNLOAD_DELAY_SECONDS) # Wait after a successful download
                    except requests.exceptions.RequestException as e:
                        print(f"  ❌ Error downloading Icon {file_url}: {e}")
                        error_count += 1
                else:
                    print(f"  ⏩ Icon already exists. Skipping.")
                    skipped_files += 1

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ❌ Error processing 'data.json' in '{folder_name}': {e}")
            error_count += 1
    
    print("\n" + "="*50)
    print("🎉 ASSET DOWNLOAD COMPLETE! 🎉")
    print(f"Total SWFs downloaded: {downloaded_swfs}")
    print(f"Total Icons downloaded: {downloaded_icons}")
    print(f"Files already present (skipped): {skipped_files}")
    print(f"Errors encountered: {error_count}")
    print("="*50)


if __name__ == "__main__":
    download_all_assets()