import json
import os
import sys

# We add the base path so that Python find our packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api_client.meli_client import MeliClient


def main():
    print("Starting the connection test to the MercadoLibre API...")
    client = MeliClient()

    # Category MLA1055: Smartphones
    category_id = "MLA1055"

    # We extract a little batch of items (10) to test the connection and structure
    print(f"Fetching items from category {category_id}...")
    items = client.get_items_by_category(category_id, max_items=10)

    if items:
        print(f"Successfully fetched {len(items)} items from category {category_id}.")

        # We save the raw response (simulated bronze layer) in a local JSON file
        output_file = "sample_items.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)

        print(f"\nData saved in the file: '{output_file}'")
        print(
            "Review this file to analyze the complexity of the nested JSON structure."
        )
    else:
        print("Failed to fetch the data. Please check the console for any error.")


if __name__ == "__main__":
    main()
