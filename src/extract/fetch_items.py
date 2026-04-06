import os
import time
import json
import logging
from datetime import datetime
from src.api_client.meli_client import MeliClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

REQUEST_DELAY = 1


def get_product_ids_from_file(filepath="target_products.txt"):
    """
    Phase 1: Reads the IDs provided by the business team from a local text file.
    """
    if not os.path.exists(filepath):
        logging.error(f"File '{filepath}' not found.")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        product_ids = [line.strip() for line in f if line.strip()]

    logging.info(f"Loaded {len(product_ids)} IDs from {filepath}")
    return product_ids


def fetch_items_one_by_one(client, product_ids):
    """
    Phase 2: Fetches items one by one using the Multiget endpoint.
    MercadoLibre not support Multiget for /products, so we need to fetch items one by one.
    """
    collected_data = []

    for i, prod_id in enumerate(product_ids, 1):
        logging.info(f"[{i}/{len(product_ids)}] Fetching {prod_id}...")

        # We use trhe generic method aiming to the catalog
        data = client.get(f"products/{prod_id}")

        if data:
            collected_data.append(data)
        else:
            logging.warning(f"Error fetching data for ID: {prod_id}")

        # Delay to avoid overwhelming the API
        time.sleep(REQUEST_DELAY)

    return collected_data


def main():
    print("Starting Enrichment Pipeline - Bronze Layer...")

    product_ids = get_product_ids_from_file()
    if not product_ids:
        return

    client = MeliClient()

    print(f"\nStarting catalog extraction for {len(product_ids)} products...")
    collected_data = fetch_items_one_by_one(client, product_ids)

    if collected_data:
        # Dinamic directory creation
        output_dir = os.path.join("data", "raw")
        os.makedirs(
            output_dir, exist_ok=True
        )  # Create the directory if it doesn't exist

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            output_dir, f"bronze_smartphones_data_{timestamp}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, indent=4, ensure_ascii=False)

        print("\nSuccessfully completed the extraction phase!")
        print(f"  Items saved: {len(collected_data)}")
        print(f"  File generated: {output_file}")
    else:
        print("\nFailed to extract data. Please check the logs.")


if __name__ == "__main__":
    main()
