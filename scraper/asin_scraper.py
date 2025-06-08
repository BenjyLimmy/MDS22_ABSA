import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()

class AsinHandler:
    """
    Handles the discovery and extraction of Amazon Standard Identification Numbers (ASINs)
    and associated product metadata for a specified laptop brand from Amazon search results.
    Integrates with ScrapingBee for rendered HTML retrieval and BeautifulSoup for parsing.
    """

    # Mapping of supported brands to their Amazon search keyword and filter_id
    brand_filter_map = {
        "hp": ("hp", "&rh=n%3A21512780011%2Cp_123%3A308445"),
        "dell": ("dell", "&rh=n%3A21512780011%2Cp_123%3A241862"),
        "lenovo": ("lenovo", "&rh=n%3A21512780011%2Cp_123%3A391242"),
        "apple": ("apple", "&rh=n%3A21512780011%2Cp_123%3A110955"),
        "lg": ("lg", "&rh=n%3A21512780011%2Cp_123%3A46658"),
    }

    def __init__(self, brand="hp", max_asins=None):
        """
        Initializes the handler with the specified brand and maximum number of ASINs to collect.
        Loads ScrapingBee API key and Amazon cookies from environment variables.

        Args:
            brand (str): Brand key as defined in brand_filter_map.
            max_asins (int, optional): Maximum number of ASINs to collect.
        """
        self.api_key = os.getenv("SCRAPINGBEE_API_KEY")
        if not self.api_key:
            raise Exception("SCRAPINGBEE_API_KEY not set in the environment.")
        self.cookies = os.getenv("AMAZON_COOKIES", "")

        # Validate brand and set default if not found
        if brand not in self.brand_filter_map:
            print(f"Brand '{brand}' not found. Defaulting to 'hp'.")
            brand = "hp"

        brand_value, filter_id = self.brand_filter_map[brand]
        self.start_url = f"https://www.amazon.com/s?k={brand_value}+laptop{filter_id}"
        print(f"Starting URL: {self.start_url}")

        self.max_asins = int(max_asins) if max_asins is not None else None
        self.asins = []  # List to store scraped product data

    def get_page(self, url):
        """
        Fetches the rendered HTML content of the given URL using ScrapingBee.

        Args:
            url (str): The URL to fetch.

        Returns:
            bytes or None: HTML content if successful, else None.
        """
        # Prepare parameters for ScrapingBee API request
        params = {
            'api_key': self.api_key,
            'url': url,
            'block_resources': 'false',
            'cookies': self.cookies
        }
        print(f"Fetching: {url}")

        # Make the request to ScrapingBee API
        response = requests.get("https://app.scrapingbee.com/api/v1", params=params)
        if response.status_code == 200:
            print(f"Success: {url} returned HTTP {response.status_code}")
            return response.content
        else:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
            return None

    def parse_page(self, html, base_url):
        """
        Parses the HTML content to extract ASINs and associated metadata (price, image, product URL).
        Stops if the maximum ASIN count is reached.

        Args:
            html (bytes): HTML content of the page.
            base_url (str): The base URL for resolving relative product links.

        Returns:
            bool: True if max_asins reached, else False.
        """
        soup = BeautifulSoup(html, 'html.parser')
        # Select product containers matching Amazon's search result structure
        product_containers = soup.select('div[role="listitem"][data-component-type="s-search-result"]')
        for product in product_containers:
            asin = product.get("data-asin")
            if asin:
                # Extract image source
                img_src = None
                img_tag = product.select_one("img.s-image")
                if img_tag:
                    img_src = img_tag.get("src")
                # Extract price text
                price = None
                price_tag = product.select_one("div[data-cy='price-recipe'] span.a-price > span.a-offscreen")
                if price_tag:
                    price = price_tag.get_text(strip=True)
                # Extract relative product URL and convert to absolute URL
                relative_url = None
                link_tag = product.select_one("a.a-link-normal.s-no-outline")
                if link_tag:
                    relative_url = link_tag.get("href")
                product_url = urljoin(base_url, relative_url) if relative_url else None

                print(f"Found ASIN: {asin}\n")
                self.asins.append({
                    "asin": asin,
                    "price": price,
                    "image_url": img_src,
                    "product_url": product_url
                })
                # Stop if max_asins reached
                if self.max_asins and len(self.asins) >= self.max_asins:
                    return True
        return False

    def get_next_page(self, html, base_url):
        """
        Finds and returns the full URL of the next page, if available.

        Args:
            html (bytes): HTML content of the current page.
            base_url (str): The base URL for resolving relative pagination links.

        Returns:
            str or None: Full URL of the next page if available, else None.
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_page_link = soup.select_one("li.a-last a")
        if next_page_link:
            next_page_url = next_page_link.get("href")
            full_url = urljoin(base_url, next_page_url)
            print(f"Following pagination link: {full_url}")
            return full_url
        return None

    def save_asins(self):
        """
        Saves the scraped ASINs and their metadata to a JSON file in the 'scraper_results' directory.
        """
        scraper_dir = "scraper_results"
        if not os.path.exists(scraper_dir):
            os.makedirs(scraper_dir)
            print(f"Created directory: {scraper_dir}")
        output_path = os.path.join(scraper_dir, "asins.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.asins, f, ensure_ascii=False, indent=4)
        print(f"Results saved to {output_path}")

    def run(self):
        """
        Main method to orchestrate the ASIN scraping process:
        - Fetches paginated search result pages,
        - Parses ASINs and metadata,
        - Stops when quota is met or no more pages,
        - Saves results to JSON.

        Returns:
            list: List of ASIN and metadata dictionaries.
        """
        # If max_asins is zero or less, immediately write an empty JSON and return
        if self.max_asins is not None and self.max_asins <= 0:
            print(f"max_asins set to {self.max_asins}; skipping scrape and saving empty JSON.")
            self.asins = []
            self.save_asins()
            return self.asins

        current_url = self.start_url
        while current_url:
            html = self.get_page(current_url)
            if not html:
                break
            # Parse the current page and check if the max ASIN count is reached
            stop = self.parse_page(html, current_url)
            if stop:
                print(f"Reached maximum ASIN limit: {self.max_asins}")
                break
            # Get URL of the next page (if available)
            next_url = self.get_next_page(html, current_url)
            if not next_url:
                print("No further pages found.")
                break
            current_url = next_url
        self.save_asins()
        return self.asins

if __name__ == "__main__":
    load_dotenv()
    # Initialize AsinHandler with desired brand and maximum number of ASINs to scrape
    handler = AsinHandler(brand="hp", max_asins=3)
    results = handler.run()
    print("\nTotal ASINs scraped:", len(results))
    print(results)
