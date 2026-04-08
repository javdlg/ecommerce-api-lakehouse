import os
import glob
import json

# Configuration
BRONZE_DIR = os.path.join("data", "raw")


def get_latest_bronze_file(directory):
    """
    Finds the most recently created JSON file from the bronze layer.
    """
    search_pattern = os.path.join(directory, "bronze_layer_smartphones_*.json")
    files = glob.glob(search_pattern)
    return max(files, key=os.path.getctime) if files else None


def explore_unique_attributes():
    """
    Reads the raw JSON and prints every unique attribute ID found across all products to help map the silver layer schema.
    """
    print("Starting data profiling: Extracting unique attributes...")

    filepath = get_latest_bronze_file(BRONZE_DIR)
    if not filepath:
        print("Error: No bronze files found in data/raw.")
        return

    print(f"Analyzing file: {filepath}\n")

    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Use a set to automatically keep only unique values
    unique_attributes = set()

    for item in raw_data:
        attributes = item.get("attributes", [])
        for attr in attributes:
            attr_id = attr.get("id")
            if attr_id:
                unique_attributes.add(attr_id)

    print(f"Total unique attributes: {len(unique_attributes)}")
    print("Available columns for silver layer:")
    print("-" * 40)

    # Print sorted alphabetically for easy reading
    for attr in sorted(unique_attributes):
        print(f" - {attr}")


if __name__ == "__main__":
    explore_unique_attributes()