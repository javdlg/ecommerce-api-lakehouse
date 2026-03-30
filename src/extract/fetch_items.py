import json
import logging
from src.api_client.meli_client import MeliClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    print("Initializing direct extraction by Item ID...")
    client = MeliClient()

    # List of real cell phone IDs on Mercado Libre Argentina (MLA)
    # You can replace these with any valid item IDs from the MLA marketplace
    item_ids = [
        "MLA63468990",
        "MLA2071412843",
        "MLA2060138354",
    ]

    collected_data = []

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
