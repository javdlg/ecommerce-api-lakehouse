import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MeliClient:
    def __init__(self):
        """
        Initializes the MeliClient.
        Uses a Session to reuse the underlying TCP connection,
        improving performance when making multiple requests.
        """
        self.base_url = "https://api.mercadolibre.com"
        self.session = requests.Session()

        self.access_token = os.getenv("MELI_ACCESS_TOKEN")

        if not self.access_token:
            logging.error("MELI_ACCESS_TOKEN not found in environment variables.")

        # Headers configuration with the token and other necessary headers for MercadoLibre API
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            }
        )

    def _make_request(self, endpoint, params=None, max_retries=3):
        """
        Internal method to make HTTP requests with retry logic.
        Handles temporary errors and rate limits (429).
        """
        url = f"{self.base_url}/{endpoint}"
        attempt = 0

        while attempt < max_retries:
            try:
                response = self.session.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429 or response.status_code >= 500:
                    attempt += 1
                    sleep_time = 2 ** attempt
                    logging.warning(
                        f"Error {response.status_code}. Retrying in {sleep_time}s... "
                        f"(Attempt {attempt}/{max_retries})"
                    )
                    time.sleep(sleep_time)

                else:
                    logging.error(f"HTTP error {response.status_code}: {response.text}")
                    return None  # No retries for 4xx errors (except 429)

            except requests.exceptions.RequestException as e:
                attempt += 1
                sleep_time = 2 ** attempt
                logging.warning(
                    f"Network exception: {e}. Retrying in {sleep_time}s... "
                    f"(Attempt {attempt}/{max_retries})"
                )
                time.sleep(sleep_time)

        # Explicit return None after exhausting all retries
        logging.error(f"Max retries reached ({max_retries}) for {url}")
        return None

    def get(self, endpoint, params=None):
        """
        Generic GET method for flexible endpoint calls.
        Used by fetch_items.py for the /search discovery phase.
        Strips leading slash to keep consistency with base_url.
        """
        clean_endpoint = endpoint.lstrip("/")
        return self._make_request(clean_endpoint, params=params)

    def get_item(self, item_id):
        """
        Fetches a single product by its ID.
        """
        endpoint = f"items/{item_id}"
        logging.info(f"Fetching item: {item_id}")
        return self._make_request(endpoint)

    def get_items_batch(self, item_ids):
        """
        Fetches up to 20 items in a single request using
        the /items?ids= batch endpoint — much more efficient
        than one request per item.
        Returns a list of {code, body} objects.
        """
        if not item_ids:
            return []

        # API hard limit: max 20 IDs per batch request
        batch = item_ids[:20]
        if len(item_ids) > 20:
            logging.warning(
                f"get_items_batch supports max 20 IDs. "
                f"Received {len(item_ids)}, trimming to 20."
            )

        ids_str = ",".join(batch)
        endpoint = "items"
        logging.info(f"Fetching batch of {len(batch)} items...")
        return self._make_request(endpoint, params={"ids": ids_str})

    def get_items_by_category(self, category_id, max_items=150):
        """
        Fetches items from a specific category, handling pagination.
        """
        endpoint = "sites/MLA/search"
        all_items = []
        offset = 0
        limit = 50

        logging.info(f"Starting extraction for category: {category_id}")

        while len(all_items) < max_items:
            params = {"category": category_id, "offset": offset, "limit": limit}
            data = self._make_request(endpoint, params=params)

            if not data or not data.get("results"):
                logging.info("No more results available for this category.")
                break

            results = data["results"]
            all_items.extend(results)
            logging.info(
                f"Fetched {len(results)} items. "
                f"Total accumulated: {len(all_items)}"
            )

            offset += limit
            time.sleep(0.5)

        return all_items[:max_items]