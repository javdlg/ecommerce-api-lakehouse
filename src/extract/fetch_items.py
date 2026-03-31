import os
import time
import json
import logging
from datetime import datetime
from src.api_client.meli_client import MeliClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BATCH_SIZE = 20
REQUEST_DELAY = 1

def get_product_ids_from_file(filepath="target_products.txt"):
    """
    Phase 1: Reads the IDs provided by the business team from a local text file.
    """
    if not os.path.exists(filepath):
        logging.error(f"No se encontró el archivo '{filepath}'.")
        return []
        
    with open(filepath, "r", encoding="utf-8") as f:
        product_ids = [line.strip() for line in f if line.strip()]
        
    logging.info(f"Se cargaron {len(product_ids)} IDs desde {filepath}")
    return product_ids

def fetch_items_in_batches(client, product_ids):
    """
    Phase 2: Uses Multiget to extract 20 products per request.
    """
    collected_data = []
    total_batches = (len(product_ids) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num, i in enumerate(range(0, len(product_ids), BATCH_SIZE), 1):
        batch = product_ids[i : i + BATCH_SIZE]
        logging.info(f"[Batch {batch_num}/{total_batches}] Downloading {len(batch)} items...")

        # Call the super efficient method of your new client
        response = client.get_items_batch(batch)

        if response:
            # The multiget API returns a list of objects {code: 200, body: {...}}
            for entry in response:
                if entry.get("code") == 200:
                    collected_data.append(entry.get("body"))
                else:
                    logging.warning(f"Error in a batch item: {entry.get('code')}")

        time.sleep(REQUEST_DELAY)

    return collected_data

def main():
    print("Starting Enrichment Pipeline - Bronze Layer...")
    
    product_ids = get_product_ids_from_file()
    if not product_ids:
        return

    # Use the new, robust client with Session
    client = MeliClient()
    
    print(f"\nStarting batch extraction for {len(product_ids)} products...")
    collected_data = fetch_items_in_batches(client, product_ids)
            
    if collected_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bronze_layer_smartphones_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, indent=4, ensure_ascii=False)
            
        print("\nPipeline completed successfully!")
        print(f"  Items saved : {len(collected_data)}")
        print(f"  File generated: {output_file}")
    else:
        print("\nExtraction failed. Please check the logs.")

if __name__ == "__main__":
    main()