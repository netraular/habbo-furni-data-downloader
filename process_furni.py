# dependencies/habbo-furni-data-downloader/process_furni.py

import json
import os
import time
from pathlib import Path

def sanitize_filename(filename):
    """
    Removes or replaces characters that are invalid in Windows folder names
    to prevent errors when creating directories.
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    return sanitized

def process_and_save_furni(input_dir: Path, output_dir: Path):
    """
    Reads the COM and ES JSON files, merges them, and saves each furni
    into its own dedicated folder.
    """
    print("\nStarting the furni data processing script...")

    COM_FILE = input_dir / "COM_furnis.json"
    ES_FILE = input_dir / "ES_furnis.json"

    try:
        with open(COM_FILE, 'r', encoding='utf-8') as f:
            com_furnis = json.load(f)
        print(f"✔️ Loaded '{COM_FILE}' ({len(com_furnis)} furni).")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ ERROR loading '{COM_FILE}': {e}. Please run the download step first.")
        return False

    try:
        with open(ES_FILE, 'r', encoding='utf-8') as f:
            es_furnis = json.load(f)
        print(f"✔️ Loaded '{ES_FILE}' ({len(es_furnis)} furni).")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ ERROR loading '{ES_FILE}': {e}. Please run the download step first.")
        return False

    print("\nBuilding a lookup map for Spanish data...")
    es_data_map = {
        furni["classname"]: {
            "name": furni["hotelData"].get("name", ""),
            "description": furni["hotelData"].get("description", "")
        }
        for furni in es_furnis if furni.get("classname") and "hotelData" in furni
    }
    print(f"✔️ Map created with {len(es_data_map)} unique entries.")

    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print(f"\nCreated output directory: '{output_dir}'")

    print(f"\nProcessing and saving {len(com_furnis)} furni...")
    unmatched_furni_count = 0
    start_time = time.time()

    for i, furni in enumerate(com_furnis):
        classname = furni.get("classname")
        if not classname:
            continue

        if classname in es_data_map:
            furni["hotelData"]["name_es"] = es_data_map[classname]["name"]
            furni["hotelData"]["description_es"] = es_data_map[classname]["description"]
        else:
            furni["hotelData"]["name_es"] = ""
            furni["hotelData"]["description_es"] = ""
            unmatched_furni_count += 1
        
        sanitized_classname = sanitize_filename(classname)
        furni_folder_path = output_dir / sanitized_classname
        os.makedirs(furni_folder_path, exist_ok=True)
        furni_json_path = furni_folder_path / "data.json"
        with open(furni_json_path, 'w', encoding='utf-8') as f:
            json.dump(furni, f, indent=2, ensure_ascii=False)

    end_time = time.time()
    print("\n" + "="*50)
    print("🎉 PROCESSING COMPLETE! 🎉")
    print(f"Total furni processed: {len(com_furnis)}")
    print(f"Furni with no Spanish match: {unmatched_furni_count}")
    print(f"Total time: {end_time - start_time:.2f} seconds.")
    print(f"All data saved in '{output_dir}'.")
    print("="*50)
    return True