import os
import timing
import logging
import requests

# Basic logging config to view what the code does
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MeliClient:
    def __init__(self):
        """
        Initializes the MeliClient.
        We use a Sesion for reuse the underlying TCP connection, improving performance when making multiple requests
        """
        self.base_url = "https://api.mercadolibre.com"
        self.session = requests.Session()

        # Example of how you can load a token if the endpoint deserves it in the future
        # self.token = os.getenv("MELI_ACCESS_TOKEN", "")
        # self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _make_request(self, endpoint, params=None, max_retries=3):
        """
        Internal method to make HTTP requests with retry logic.
        Handles temporal errors and rate limits (429)
        """
        url= f"{self.base_url}/{endpoint}"
        attempt = 0 

        while attempt < max_retries:
            try:
                response = self.session.get(url, params=params, timeout=10)
            
                # If the response is sucessful (200 OK) we return the JSON
                if response.status_code == 200:
                    return response.json()

                # If the response is a rate limit error (429) or server error (500+)
                elif response.status_code == 429 or response.status_code >= 500:
                    attempt += 1
                    # Exponential backoff: wait 2s, then 4s, then 8s
                    sleep_time = 2 ** attempt
                    logging.warning(f"Error {response.status_code}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
            
                # For other errors like 404, 401, 403, etc. we stop the execution
                else:
                    logging.error(f"HTTP error {response.status_code}: {response.text}")
                    response.raise_for_status()

            except request.exceptions.RequestException as e:
                attempt += 1
                logging.warning(f"Network exception: {e}. Retrying... (Attempt {attempt}/{max_retries})")
                sleep_time = 2 ** attempt

        logging.error(f"The max retries was reached ({max_retries}) for {url}")      
        return None
                
