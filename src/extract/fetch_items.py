import os
import time
import json
import logging
from datetime import datetime
from src.api_client.meli_client import MeliClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ─── Config ───────────────────────────────────────────────────────────────────
SITE_ID = "MLA"
SEARCH_QUERY = "smartphone"  # Modify according to use case
CATEGORY_ID = None  # Optional: e.g., "MLA1055" for Electronics
MAX_RESULTS = 200  # Max IDs to extract via search
BATCH_SIZE = 20  # Max supported by /items?ids=
REQUEST_DELAY = 0.5  # Seconds between requests
MAX_RETRIES = 3  # Retries on failure


# ─── Phase 1: Discovery of IDs via Search API ─────────────────────────────
def fetch_product_ids_from_api(
    client, query=SEARCH_QUERY, category=CATEGORY_ID, max_results=MAX_RESULTS
):
    """
    Replaces the manual txt file: discovers product IDs using
    the /search endpoint with pagination.
    """
    all_ids = []
    limit = 50  # Max per page according to ML API
    offset = 0

    logging.info(
        f"Discovering IDs — query='{query}', category='{category}', max={max_results}"
    )

    while offset < max_results:
        params = {"limit": limit, "offset": offset}
        if query:
            params["q"] = query
        if category:
            params["category"] = category

        # Use the existing client method if it already has search,
        # or make the request directly with its authenticated session
        response = client.get(f"/sites/{SITE_ID}/search", params=params)

        if not response:
            logging.warning(f"Empty response at offset {offset}. Stopping pagination.")
            break

        results = response.get("results", [])
        if not results:
            break

        batch_ids = [item["id"] for item in results]
        all_ids.extend(batch_ids)
        logging.info(
            f"  Page offset={offset}: fetched {len(batch_ids)} IDs (total so far: {len(all_ids)})"
        )

        # If ML returns fewer items than the limit, we've reached the end
        if len(results) < limit:
            break

        offset += limit
        time.sleep(REQUEST_DELAY)

    logging.info(f"Discovery complete: {len(all_ids)} IDs found.")
    return all_ids


# ─── Phase 2: Enrichment in batches ─────────────────────────────────────────
def fetch_items_in_batches(client, product_ids, batch_size=BATCH_SIZE):
    """
    Replaces the one-by-one loop: fetches up to 20 items per request
    using the /items?ids= batch endpoint.
    """
    collected_data = []
    total_batches = (len(product_ids) + batch_size - 1) // batch_size

    for batch_num, i in enumerate(range(0, len(product_ids), batch_size), 1):
        batch = product_ids[i : i + batch_size]
        ids_str = ",".join(batch)

        logging.info(
            f"[Batch {batch_num}/{total_batches}] Fetching {len(batch)} items..."
        )

        # Retry with exponential backoff
        for attempt in range(1, MAX_RETRIES + 1):
            response = client.get("/items", params={"ids": ids_str})

            if response is not None:
                break

            wait = 2**attempt
            logging.warning(f"  Attempt {attempt} failed. Retrying in {wait}s...")
            time.sleep(wait)
        else:
            logging.error(
                f"  Batch {batch_num} failed after {MAX_RETRIES} retries. Skipping."
            )
            continue

        # The response is a list of objects {code, body}
        for entry in response:
            if entry.get("code") == 200:
                collected_data.append(entry["body"])
            else:
                logging.warning(
                    f"  Item error — code {entry.get('code')}: {entry.get('body', {}).get('id', '?')}"
                )

        time.sleep(REQUEST_DELAY)

    logging.info(f"Enrichment complete: {len(collected_data)} items collected.")
    return collected_data


# ─── Phase 3: Persistence in Bronze Layer ─────────────────────────────────────
def save_bronze_layer(data, query=SEARCH_QUERY):
    """
    Saves the raw JSON with a timestamp to avoid overwriting previous runs.
    """
    if not data:
        logging.error("No data to save.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_")
    output_file = f"bronze_layer_{safe_query}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logging.info(f"Bronze layer saved: {output_file} ({len(data)} records)")
    return output_file


# ─── Main orchestrator ─────────────────────────────────────────────────────
def main():
    print("Starting Enrichment Pipeline - Bronze Layer...")

    client = MeliClient()

    # Phase 1: Automatic discovery of IDs (replaces the manual .txt)
    product_ids = fetch_product_ids_from_api(client)

    if not product_ids:
        logging.error("No IDs discovered. Aborting pipeline.")
        return

    # Phase 2: Enrichment in batches
    print(f"\nStarting batch enrichment for {len(product_ids)} products...")
    collected_data = fetch_items_in_batches(client, product_ids)

    # Phase 3: Persistence
    output_file = save_bronze_layer(collected_data)

    if output_file:
        print("\nPipeline completed successfully!")
        print(f"  IDs discovered : {len(product_ids)}")
        print(f"  Items saved    : {len(collected_data)}")
        print(f"  Output file    : {output_file}")
    else:
        print("\nPipeline failed. Check the logs.")


if __name__ == "__main__":
    main()
