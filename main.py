# main.py

import os
import sys
import shutil
import argparse
from pathlib import Path
from dotenv import load_dotenv

# --- 1. SETUP ---
load_dotenv()

# --- Configuration of Default Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_ASSETS_DIR = PROJECT_ROOT / "assets"
DEFAULT_METADATA_RAW_DIR = DEFAULT_ASSETS_DIR / "metadata_raw"
DEFAULT_FURNI_DATABASE_DIR = DEFAULT_ASSETS_DIR / "furni_database"

# Path to submodule scripts
SUBMODULE_DIR = PROJECT_ROOT / "dependencies" / "habbo-furni-data-downloader"
HABBOFURNI_API_TOKEN = os.getenv("HABBOFURNI_API_TOKEN")

# --- Import functions from other scripts ---
sys.path.append(str(SUBMODULE_DIR))
try:
    from download_furni_data import download_furni_by_hotel, HOTELS
    from process_furni import process_and_save_furni
except ImportError as e:
    print(f"❌ ERROR: Could not import from submodule scripts: {e}")
    sys.exit(1)
from download_assets import download_all_assets


# --- 2. DEFINE PIPELINE STEPS ---

def step_1_fetch_metadata(output_dir: Path):
    print("\n--- [Step 1] Downloading furni metadata from API ---")
    if not HABBOFURNI_API_TOKEN:
        print("❌ ERROR: 'HABBOFURNI_API_TOKEN' not found in your .env file.")
        return False
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading data for Habbo.com to '{output_dir}'...")
    hotel_com = next((h for h in HOTELS if h["short_name"] == "COM"), None)
    if not download_furni_by_hotel(hotel_com, HABBOFURNI_API_TOKEN, output_dir):
        return False
    
    print(f"\nDownloading data for Habbo.es to '{output_dir}'...")
    hotel_es = next((h for h in HOTELS if h["short_name"] == "ES"), None)
    if not download_furni_by_hotel(hotel_es, HABBOFURNI_API_TOKEN, output_dir):
        return False
    print("\n✔️ Metadata download complete.")
    return True

def step_2_process_metadata(input_dir: Path, output_dir: Path):
    print("\n--- [Step 2] Processing and organizing metadata ---")
    if not process_and_save_furni(input_dir, output_dir):
        return False
    print("✔️ Metadata processing complete.")
    return True

def step_3_download_assets(database_dir: Path, download_swfs: bool, download_icons: bool):
    print("\n--- [Step 3] Downloading SWF and Icon assets ---")
    download_all_assets(database_dir, download_swfs, download_icons)
    print("✔️ Asset download step finished.")
    return True


# --- 3. RUN THE PIPELINE ---

def main():
    parser = argparse.ArgumentParser(
        description="Full pipeline to download and process Habbo furni data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Folder arguments
    parser.add_argument('--raw-dir', type=Path, default=DEFAULT_METADATA_RAW_DIR, help="Directory for raw downloaded JSON files.")
    parser.add_argument('--database-dir', type=Path, default=DEFAULT_FURNI_DATABASE_DIR, help="Directory for the processed furni database.")
    
    # Step control arguments
    parser.add_argument('--start-at', type=int, choices=[1, 2, 3], default=1, help="Pipeline step to start from (1: Fetch, 2: Process, 3: Download Assets).")
    
    # Asset download arguments (optional)
    parser.add_argument('--download-swf', action='store_true', help="Enable downloading of .swf asset files during Step 3.")
    parser.add_argument('--download-icons', action='store_true', help="Enable downloading of icon .png files during Step 3.")
    
    args = parser.parse_args()

    print("======================================================")
    print("=      HABBO FURNI & ASSET PIPELINE STARTING     =")
    print(f"=      Starting from step: {args.start_at}                  =")
    print(f"=      Raw data directory: {args.raw_dir}      =")
    print(f"=      Final database directory: {args.database_dir} =")
    print(f"=      Download SWFs: {'Yes' if args.download_swf else 'No'}                       =")
    print(f"=      Download Icons: {'Yes' if args.download_icons else 'No'}                      =")
    print("======================================================")

    if args.start_at <= 1:
        if not step_1_fetch_metadata(args.raw_dir): sys.exit(1)
    
    if args.start_at <= 2:
        if not step_2_process_metadata(args.raw_dir, args.database_dir): sys.exit(1)

    if args.start_at <= 3:
        if args.download_swf or args.download_icons:
            step_3_download_assets(args.database_dir, download_swfs=args.download_swf, download_icons=args.download_icons)
        else:
            print("\n--- [Step 3] Skipped: No asset download flags (--download-swf, --download-icons) were provided. ---")

    print("\n==========================================")
    print("=        PIPELINE COMPLETED SUCCESSFULLY       =")
    print("==========================================")

if __name__ == "__main__":
    main()