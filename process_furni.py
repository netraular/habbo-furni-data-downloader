# process_furni.py

import json
import os
import time

# --- CONFIGURATION ---
# Directory where the raw downloaded JSON files are located
INPUT_DIR = "habbo_furni_data"
# The base file (English) and the file to merge from (Spanish)
COM_FILE = os.path.join(INPUT_DIR, "COM_furnis.json")
ES_FILE = os.path.join(INPUT_DIR, "ES_furnis.json")
# The main output directory for the processed, structured data
OUTPUT_DIR = "furni_database"


def sanitize_filename(filename):
    """
    Removes or replaces characters that are invalid in Windows folder names
    to prevent errors when creating directories.
    """
    # List of characters forbidden in Windows folder/file names
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = filename
    for char in invalid_chars:
        # We replace each invalid character with an underscore
        sanitized = sanitized.replace(char, '_')
    return sanitized


def process_and_save_furni():
    """
    Reads the COM and ES JSON files, merges the name and description fields,
    and saves each resulting furni object into its own dedicated folder.
    """
    print("Starting the furni data processing script...")

    # --- STEP 1: Load the data from the JSON files ---
    try:
        with open(COM_FILE, 'r', encoding='utf-8') as f:
            com_furnis = json.load(f)
        print(f"✔️ Successfully loaded '{COM_FILE}' ({len(com_furnis)} furni).")
    except FileNotFoundError:
        print(f"❌ ERROR: The file '{COM_FILE}' was not found. Please run the download script first.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: The file '{COM_FILE}' is not a valid JSON file.")
        return

    try:
        with open(ES_FILE, 'r', encoding='utf-8') as f:
            es_furnis = json.load(f)
        print(f"✔️ Successfully loaded '{ES_FILE}' ({len(es_furnis)} furni).")
    except FileNotFoundError:
        print(f"❌ ERROR: The file '{ES_FILE}' was not found. Please run the download script first.")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: The file '{ES_FILE}' is not a valid JSON file.")
        return

    # --- STEP 2: Create a lookup dictionary for the Spanish data for faster access ---
    # This is much more efficient than searching the list for every single item.
    print("\nBuilding a lookup map for Spanish data...")
    es_data_map = {
        furni["classname"]: {
            "name": furni["hotelData"].get("name", ""),
            "description": furni["hotelData"].get("description", "")
        }
        for furni in es_furnis if furni.get("classname") and "hotelData" in furni
    }
    print(f"✔️ Map created with {len(es_data_map)} unique entries.")

    # --- STEP 3: Create the main output directory if it doesn't exist ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"\nCreated output directory: '{OUTPUT_DIR}'")

    # --- STEP 4: Iterate, merge data, and save individual files ---
    print(f"\nProcessing and saving {len(com_furnis)} furni...")
    unmatched_furni_count = 0
    start_time = time.time()

    for i, furni in enumerate(com_furnis):
        classname = furni.get("classname")
        if not classname:
            print(f"⚠️ Warning: Found a furni at index {i} with no 'classname'. Skipping.")
            continue

        # Merge the data: add Spanish name/description to the English furni object
        if classname in es_data_map:
            furni["hotelData"]["name_es"] = es_data_map[classname]["name"]
            furni["hotelData"]["description_es"] = es_data_map[classname]["description"]
        else:
            # If no match is found, add empty fields to maintain a consistent structure
            furni["hotelData"]["name_es"] = ""
            furni["hotelData"]["description_es"] = ""
            unmatched_furni_count += 1
        
        # Sanitize the classname before using it as a folder name to avoid OS errors
        sanitized_classname = sanitize_filename(classname)
            
        # Create the specific folder for this furni
        furni_folder_path = os.path.join(OUTPUT_DIR, sanitized_classname)
        os.makedirs(furni_folder_path, exist_ok=True)

        # Save the combined data into its own JSON file
        furni_json_path = os.path.join(furni_folder_path, "data.json")
        with open(furni_json_path, 'w', encoding='utf-8') as f:
            json.dump(furni, f, indent=2, ensure_ascii=False)

    end_time = time.time()
    print("\n" + "="*50)
    print("🎉 PROCESSING COMPLETE! 🎉")
    print(f"Total furni processed: {len(com_furnis)}")
    print(f"Furni with no Spanish match: {unmatched_furni_count}")
    print(f"Total time: {end_time - start_time:.2f} seconds.")
    print(f"All data has been saved in the '{OUTPUT_DIR}' folder.")
    print("="*50)


if __name__ == "__main__":
    process_and_save_furni()