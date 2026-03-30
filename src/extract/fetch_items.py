import time
import json
import logging
import requests
from src.api_client.meli_client import MeliClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_product_ids_from_search(category="MLA1055", limit=50):
    """
    The scout: This function uses the public API (without token) to evade the firrewall and collect the IDs from the products catalog
    """
    url = f"https://api.mercadolibre.com/sites/MLA/search?category={category}&limit={limit}"

    # We use a browser user-agent, but without the authentication: Bearer
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    logging.info(f"Tracking products in category {category}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(
            f"Failed to track products. HTTP {response.status_code}: {response.text}"
        )
        return []

    data = response.json()
    results = data.get("results", [])

    product_ids = []
    for items in results:
        # We search for the specific catalog ID (Product), no the item ID (Publication)
        cat_id = items.get("catalog_product_id")

        # We filter to ensure that exists and is not duplicated
        if cat_id and cat_id not in product_ids:
            product_ids.append(cat_id)

    logging.info(
        f"Found {len(product_ids)} unique and valid product IDs in category {category}"
    )
    return product_ids


def main():
    print("Initializing batch extraction - Bronze layer...")
    client = MeliClient()

    # 1. The scout goes to find the product IDs in the category (first with 50)
    product_ids = get_product_ids_from_search(limit=50)

    if not product_ids:
        logging.error("No product IDs found. Exiting.")
        return

    # 2. We initialize our authenticated client to fetch the item details
    client = MeliClient()
    collected_data = []

    # 3. The worker processes the list
    print(f"Extracting details for {len(product_ids)} products...")

    # MODIFY ALL THE CODE BELOW LATER #

    for item_id in item_ids:
        data = client.get_item(item_id)
        if data:
            collected_data.append(data)
        else:
            logging.warning(f"No data found for item ID: {item_id}")

    if collected_data:
        output_file = "sample_items.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(collected_data, f, indent=4, ensure_ascii=False)
        print(f"\n¡Éxit! {len(collected_data)} products saved in {output_file}")
    else:
        print("\nFailed to extract any data. Check the logs.")


if __name__ == "__main__":
    main()
