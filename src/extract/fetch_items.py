import os
import time
import json
import logging
from src.api_client.meli_client import MeliClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_product_ids_from_file(filepath="target_products.txt"):
    """
    Simulates the seeding of product IDs by reading them from a local text file.
    """
    if not os.path.exists(filepath):
        logging.error(f"The file '{filepath}' was not found. Create it first!")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        # Read the lines, remove white spaces and skip empty lines
        product_ids = [line.strip() for line in f if line.strip()]

    logging.info(f"Loaded {len(product_ids)} IDs from {filepath}")
    return product_ids


def main():
    print("Starting Enrichment Pipeline - Bronze Layer...")

    # 1. Read the seed IDs from our local file
    product_ids = get_product_ids_from_file()

    if not product_ids:
        logging.error("No IDs to process. Aborting the batch.")
        return

    # 2. Initialize our authenticated client
    client = MeliClient()
    collected_data = []

    # 3. The Worker processes the list iterating over the catalog
    print(
        f"\nStarting deep extraction in Meli API for {len(product_ids)} products..."
    )

    for i, product_id in enumerate(product_ids, 1):
        logging.info(f"[{i}/{len(product_ids)}] Downloading data from: {product_id}")
        data = client.get_item(product_id)

        if data:
            collected_data.append(data)

        # Strategic pause to avoid saturating the API
        time.sleep(1)

    # 4. Save in the Bronze Layer
    if collected_data:
        output_file = "bronze_layer_smartphones.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, indent=4, ensure_ascii=False)
        print(f"\nBatch completed successfully!")
        print(f"Saved {len(collected_data)} raw records in {output_file}")
    else:
        print("\nExtraction failed. Check the logs.")

if __name__ == "__main__":
    main()
