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
    finds the most recently created JSON file from the bronze layer directory.
    """
    search_pattern = os.path.join(directory, "bronze_smartphones_data_*.json")
    files = glob.glob(search_pattern)

    if not files:
        logging.error(f"No bronze files found in {directory}")
        return None
