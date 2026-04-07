import os
import glob
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configuration
BRONZE_DIR = os.path.join("data", "raw")
SILVER_DIR = os.path.join("data", "processed")

# We securely that the output directory exists
os.makedirs(SILVER_DIR, exist_ok=True)

SILVER_OUTPUT = os.path.join(SILVER_DIR, "silver_smartphone_data.parquet")


def get_latest_bronze_file(directory):
    """
    Finds the most recently created JSON file from the bronze layer directory.
    """
    search_pattern = os.path.join(directory, "bronze_smartphones_data_*.json")
    files = glob.glob(search_pattern)

    if not files:
        logging.error(f"No bronze files found in {directory}")
        return None

    # Get the most recent file
    latest_file = max(files, key=os.path.getctime)
    logging.info(f"Found latest bronze file: {latest_file}")

    return latest_file


def extract_attributes(attributes_list):
    """
    Mercado Libre hides the specs inside a list of dictionaries.
    This function flattens that list into a simple key-value dictionary.
    """
    extracted = {}
    if not isinstance(attributes_list, list):
        return extracted

    for attr in attributes_list:
        # We use the 'id' (e.g., 'BATTERY_CAPACITY') as the column name
        attr_id = attr.get(id)
        # And 'value_name' (e.g., '5000 mAh') as the value
        attr_value = attr.get("value_name")

        if attr_id:
            extracted[attr_id] = attr_value

    return extracted


def process_bronze_data(filepath):
    """
    Loads the JSON, flattens the nested structures, and returns a clean DataFrame.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed_records = []

    for item in raw_data:
        # 1. Extract base fields
        record = {
            "product_id": item.get("id"),
            "name": item.get("name"),
            "status": item.get("status"),
            "domain_id": item.get("domain_id"),
            "date_created": item.get("date_created"),
        }

        # 2. Extract and flatten the attributes
        attributes_dict = extract_attributes(item.get("attributes", []))
        # 3. Merge base fields with flattened attributes
        record.update(attributes_dict)
        processed_records.append(record)

    # Create the DataFrame
    df = pd.DataFrame(processed_records)
    return df


def clean_and_format_dataframe(df):
    """
    Applies silver layer transformations: filtering, casting, and dropping nulls.
    """
    # Select only the columns we actually care about for analytics
    # Note: These columns depend on the attributes ML returns
    columns_to_keep = [
        "product_id",
        "name",
        "status",
        "BRAND",
        "LINE",
        "MODEL",
        "INTERNAL_MEM",
        "BATTERY_CAPACITY",
    ]

    # Keep only columns that actually exists in the DataFrame to avoid key errors
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df_clean = df[existing_columns].copy()

    # Standarize column names (lowercase)
    df_clean.columns = [col.lower() for col in df_clean.columns]

    # Convert dates to datetime objects
    if "date_created" in df.columns:
        df_clean["date_created"] = pd.to_datetime(
            df_clean["date_created"]
        ).dt.tz_localize(None)

    # Fill missing values with a standard label
    df_clean = df_clean.fillna("N/A")

    return df_clean


def main():
    print("Starting transformation from bronze to silver layer...")

    # 1. Read
    latest_file = get_latest_bronze_file(BRONZE_DIR)
    if not latest_file:
        return

    # 2. Flatten and process
    logging.info("Loading and flattening JSON data...")
    df_raw = process_bronze_data(latest_file)

    # 3. Clean and format
    logging.info("Cleaning and formatting DataFrame...")
    df_clean = clean_and_format_dataframe(df_raw)

    # 4. Save to Parquet (highly compressed columnar format)
    logging.info(f"Saving transformed DataFrame to {SILVER_OUTPUT}")
    df_clean.to_parquet(SILVER_OUTPUT, engine="pyarrow", index=False)

    print("Silver layer transformation complete.")
    print(f"  Rows processed: {len(df_clean)}")
    print(f"  Columns created: {len(df_clean.columns)}")
    print(f"  Preview:\n{df_clean.head(3)}")


if __name__ == "__main__":
    main()
