# Habbo Furni & Asset Pipeline

This project provides a set of Python scripts to download Habbo Hotel furni metadata from the [HabboFurni.com](https://habbofurni.com/) API, process it into a structured database, and optionally download the associated SWF and icon image assets.

## Data Source

The metadata is sourced directly from the HabboFurni API, which provides comprehensive information about furniture across multiple hotels. The asset files (SWFs, PNGs) are downloaded from the URLs provided within that metadata.

*(Screenshot of the HabboFurni.com website)*


## Features

-   **Complete Pipeline**: An orchestrator script (`main.py`) runs all steps in sequence.
-   **Data Enrichment**: Combines furni data from the `.COM` (English) and `.ES` (Spanish) hotels to create a bilingual dataset.
-   **Structured Output**: Organizes each furni into its own folder, containing a `data.json` file with its merged metadata.
-   **Optional Asset Downloading**: By default, the script only prepares the metadata. You can enable SWF and/or icon downloading with simple flags.
-   **Flexible & Configurable**: Use command-line arguments to specify custom output directories and to skip steps you've already completed.
-   **Secure Configuration**: Uses a `.env` file to keep your API token safe and out of version control.

## Project Structure

```
.
├── .env                  # Your secret API token (you create this)
├── assets/               # Default output folder
│   ├── metadata_raw/     # Output of Step 1: Raw JSON files
│   └── furni_database/   # Output of Step 2 & 3: Processed folders with assets
├── dependencies/
│   └── habbo-furni-data-downloader/
│       ├── download_furni_data.py
│       └── process_furni.py
├── download_assets.py
├── main.py               # The main script to run the pipeline
├── requirements.txt
└── README.md
```

## Installation

1.  **Clone this repository.**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Ensure you have Python 3.8+ installed.**

3.  **Install the required dependencies using `pip`.**
    In the project's root folder, run:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the pipeline, you must configure your HabboFurni API token.

1.  **Get your API token** from your account on [HabboFurni.com](https://habbofurni.com/).
2.  **Create a file named `.env`** in the root directory of the project.
3.  **Add your token to the `.env` file** in the following format:

    ```
    # in .env file
    HABBOFURNI_API_TOKEN="eyJ0eXAi...your_full_token_here"
    ```

## Usage

The entire pipeline is controlled by `main.py`. By default, it will only download and process metadata. You must explicitly enable asset downloading.

### Running the Metadata-Only Pipeline

This is the default behavior. It will execute Steps 1 and 2, creating a database of `data.json` files without any SWFs or icons.

```bash
python main.py
```

### Enabling Asset Downloads

Use the `--download-swf` and `--download-icons` flags to download the assets in Step 3. You can use either one or both.

```bash
# Download metadata, process it, AND download both SWFs and icons
python main.py --download-swf --download-icons
```

### Specifying Custom Output Folders

You can control where the data is saved using the `--raw-dir` and `--database-dir` flags.

```bash
python main.py --raw-dir "D:/habbo/raw" --database-dir "D:/habbo/database" --download-swf
```

### Skipping Steps

If you have already completed some steps, use `--start-at` to resume the pipeline.

```bash
# You already have raw data, now process it and download icons
python main.py --start-at 2 --download-icons

# You have a processed database, just download the missing SWFs
python main.py --start-at 3 --download-swf
```

### Pipeline Steps Explained

-   **Step 1: Fetch Metadata**: Downloads `COM_furnis.json` and `ES_furnis.json` from the API into the `--raw-dir`.
-   **Step 2: Process Metadata**: Reads the raw JSONs, merges them, and creates a folder for each furni inside the `--database-dir`. Each folder contains a `data.json` file.
-   **Step 3: Download Assets (Optional)**: If enabled via flags, this step scans every folder in the `--database-dir`, reads its `data.json`, and downloads the corresponding SWF and/or icon files into that same folder.

#### Final Output Example

After a full run with asset downloads enabled, a folder for a single furni will look like this:

```
assets/furni_database/shelves_norja/
├── data.json              (Merged COM and ES metadata)
├── shelves_norja.swf      (Downloaded if --download-swf was used)
└── shelves_norja_icon.png (Downloaded if --download-icons was used)
```