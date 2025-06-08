import requests
import os
import json
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from scrapy import Selector
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Dict

class AmazonReviewProcessor:
    """
    Processes Amazon product reviews for a single laptop ASIN.
    Handles review scraping, star histogram analysis, stratified review sampling,
    deduplication, metadata extraction, and JSON serialization.
    """

    def __init__(self, api_key, brand: str, product_info: Dict[str, str], review_pages=5):
        """
        Initialize the processor with API key, brand, product metadata, and scrape settings.

        Args:
            api_key (str): ScrapingBee API key.
            brand (str): Brand name (used for output file naming).
            product_info (Dict[str, str]): Dict with keys 'asin', 'price', 'image_url', 'product_url'.
            review_pages (int): Number of review pages to scrape per star rating.
        """
        self.api_key = api_key
        self.brand = brand
        self.product_id = product_info.get("asin")
        self.price = product_info.get("price")
        self.image_url = product_info.get("image_url")
        self.product_url = product_info.get("product_url")
        self.pages = review_pages
        self.output_dir = "scraper_results"
        self.ensure_output_dir()

        # Counters for summary statistics
        self.total_reviews_scraped = 0
        self.scraping_success = 0
        self.scraping_failed = 0

    def ensure_output_dir(self):
        """
        Create the output directory if it does not already exist.
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

    def send_request(self, page_number, base_url=None):
        """
        Send a GET request to ScrapingBee to fetch a rendered Amazon review page.

        Args:
            page_number (int): The review page number to fetch.
            base_url (str, optional): If provided, use this as the base URL for filtered reviews.

        Returns:
            bytes or None: HTML content if successful, else None.
        """
        if base_url:
            # Update/add the pageNumber and common params in the provided URL.
            parsed = urlparse(base_url)
            qs = parse_qs(parsed.query)
            qs["pageNumber"] = [str(page_number)]
            qs.setdefault("ie", ["UTF8"])
            qs.setdefault("reviewerType", ["all_reviews"])
            new_query = urlencode(qs, doseq=True)
            url = urlunparse((parsed.scheme or "https", 
                               parsed.netloc or "www.amazon.com", 
                               parsed.path, 
                               parsed.params, 
                               new_query, 
                               parsed.fragment))
        else:
            base_url = f'https://www.amazon.com/dp/product-reviews/{self.product_id}/'
            url = f'{base_url}?ie=UTF8&reviewerType=all_reviews&pageNumber={page_number}'

        print(f"At - {url}")
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1',
            params={
                'api_key': self.api_key,
                'url': url,
                'block_resources': 'false',
                'cookies': os.getenv("AMAZON_COOKIES_3", "")
            },
        )
        print(f'URL {url} - HTTP Status Code: {response.status_code}')
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to retrieve page {page_number}")
            print(response.content)
            return None

    def scrape_reviews(self):
        """
        Scrape the main review pages for the product and combine their HTML into a single file.

        Returns:
            str: Path to the combined HTML file containing all scraped review pages.
        """
        print("Step 1: Scraping main Amazon reviews...")
        combined_soup = BeautifulSoup(
            '<html><head><title>Combined Amazon Reviews</title></head><body></body></html>',
            'html.parser'
        )
        body = combined_soup.find('body')

        for page_number in range(1, self.pages + 1):
            print(f"\nProcessing main reviews page {page_number}...")
            content = self.send_request(page_number)
            if content:
                divider = combined_soup.new_tag('div')
                divider.attrs['style'] = 'margin: 20px 0; padding: 10px; background-color: #f0f0f0; border-top: 2px solid #ccc;'
                divider.string = f'--- Main Page {page_number} ---'
                body.append(divider)
                page_soup = BeautifulSoup(content, 'html.parser')
                body.append(page_soup.body or page_soup)
                self.scraping_success += 1
            else:
                self.scraping_failed += 1
            if page_number < self.pages:
                time.sleep(2)

        html_path = os.path.join(self.output_dir, "all_reviews.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(combined_soup))
        return html_path
    
    def compute_quotas(self, sel):
        """
        Extracts the star-rating histogram from the parsed Selector and computes
        the number of reviews to sample for each star level.

        Args:
            sel (scrapy.Selector): Selector object for the HTML content.

        Returns:
            tuple: (histogram, histogram_reviews_to_scrape)
                histogram: dict mapping star level to percentage string (e.g., '5_star': '66%')
                histogram_reviews_to_scrape: dict mapping star level to review quota (e.g., '5_star': 7)
        """
        histogram = {}
        histogram_reviews_to_scrape = {}
        for li in sel.css("ul#histogramTable li"):
            aria_label = li.css("a::attr(aria-label)").get()
            if aria_label:
                match = re.search(r"(\d+)\s+stars represent (\d+)%", aria_label)
                if match:
                    star = match.group(1)
                    percent = match.group(2)  # string percent (e.g., "64")
                    reviews_to_scrape = round(float(percent) / 10)  # Example: 66% → 7
                    key = f"{star}_star"
                    histogram[key] = f"{percent}%"
                    histogram_reviews_to_scrape[key] = reviews_to_scrape
        return histogram, histogram_reviews_to_scrape
    

    def dedupe_reviews(self, reviews):
        """
        Remove duplicate reviews based on review text content.

        Args:
            reviews (list): List of review dictionaries, each with a 'review_text' key.

        Returns:
            list: List of unique review dictionaries.
        """
        unique_reviews = []
        seen_texts = set()
        for review in reviews:
            if review["review_text"] not in seen_texts:
                seen_texts.add(review["review_text"])
                unique_reviews.append(review)
        return unique_reviews
    

    def to_json(self, product_data):
        """
        Serialize a product's review and metadata dictionary to the brand's JSON file.
        Appends to the file if it exists, otherwise creates a new file.

        Args:
            product_data (dict): Dictionary containing product metadata and reviews.

        Returns:
            str: Path to the output JSON file.
        """
        json_path = os.path.join(self.output_dir, f"{self.brand}_reviews.json")
        # Load existing data if file exists, else start a new list
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as infile:
                try:
                    existing_data = json.load(infile)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []
        existing_data.append(product_data)
        with open(json_path, "w", encoding="utf-8") as outfile:
            json.dump(existing_data, outfile, ensure_ascii=False, indent=4)
        print(f"Saved product data to {json_path}")
        return json_path


    def parse_reviews(self, html_path):
        """
        Parse reviews from the combined HTML, then for each star rating,
        scrape additional filtered reviews and merge all unique reviews.

        Args:
            html_path (str): Path to the combined review HTML file.

        Returns:
            str: Path to the output JSON file containing all structured review data.
        """
        print("\nStep 2: Parsing reviews from HTML...")
        with open(html_path, "r", encoding="utf-8") as file:
            html = file.read()
        sel = Selector(text=html)
        try:
            # --- Extract star-rating histogram and compute per-star quotas ---
            histogram, histogram_reviews_to_scrape = self.compute_quotas(sel)
            print("Calculated reviews to scrape per star:", histogram_reviews_to_scrape)

            # --- For each star rating, scrape additional reviews using pagination ---
            additional_reviews = []
            for star, count_needed in histogram_reviews_to_scrape.items():
                # Retrieve the base URL for this star rating from histogram info.
                star_url = None
                for li in sel.css("ul#histogramTable li"):
                    aria_label = li.css("a::attr(aria-label)").get()
                    if aria_label and star.startswith(aria_label.split()[0]):  # e.g., "5" for "5_star"
                        href = li.css("a::attr(href)").get()
                        if href:
                            star_url = urljoin("https://www.amazon.com", href)
                            break

                print(f"\nScraping up to {count_needed} reviews for {star} rating from base URL: {star_url}\n")
                if star_url and count_needed > 0:
                    star_reviews = []
                    for page in range(1, self.pages + 1):
                        page_content = self.send_request(page, base_url=star_url)
                        if page_content:
                            page_soup = BeautifulSoup(page_content, 'html.parser')
                            review_elements = page_soup.select("li[data-hook='review']")
                            for rev in review_elements:
                                review_text_tag = rev.select_one("span[data-hook='review-body'] span")
                                reviewer_name_tag = rev.select_one("a.a-profile > div.a-profile-content > span.a-profile-name")
                                star_rating_tag = rev.select_one("i[data-hook='review-star-rating'] span.a-icon-alt")
                                review_date_tag = rev.select_one("span[data-hook='review-date']")

                                # Extract review fields
                                if review_text_tag:
                                    review_text = review_text_tag.get_text(strip=True)
                                    reviewer_name = reviewer_name_tag.get_text(strip=True) if reviewer_name_tag else ""
                                    star_rating = star_rating_tag.get_text(strip=True) if star_rating_tag else ""
                                    review_date = review_date_tag.get_text(strip=True) if review_date_tag else ""
                                    star_reviews.append({
                                        "reviewer_name": reviewer_name,
                                        "star_rating": star_rating,
                                        "review_date": review_date,
                                        "review_text": review_text
                                    })
                                if len(star_reviews) >= count_needed:
                                    break
                        else:
                            print(f"Failed to retrieve page {page} for {star} reviews.")
                        if len(star_reviews) >= count_needed:
                            break
                        time.sleep(1)
                    print(f"Collected {len(star_reviews)} reviews for {star} rating.")
                    additional_reviews.extend(star_reviews)
                else:
                    print(f"No reviews to scrape for {star} rating.")

            # --- Remove duplicate reviews ---
            combined_reviews = self.dedupe_reviews(additional_reviews)
            self.total_reviews_scraped = len(combined_reviews)

            # --- Extract additional product details ---
            title = sel.css("h1.product-info-title a::text").get()
            average_rating = sel.css("i[data-hook='average-star-rating'] span.a-icon-alt::text").get()
            review_count = sel.css("div[data-hook='total-review-count'] span::text").get()

            # --- Merge all data into a product_data dictionary ---
            product_data = {
                "title": title,
                "product_id": self.product_id,
                "price": self.price,
                "image_url": self.image_url,
                "product_url": self.product_url,
                "average_rating": average_rating,
                "review_count": review_count,
                "histogram": histogram,
                "histogram_reviews_to_scrape": histogram_reviews_to_scrape,
                "review": combined_reviews
            }

        except Exception as e:
            print(f"Error while scraping: {e}")
            self.scraping_failed += 1
            product_data = {}   # Empty product data in case of error

        # Save the product data into a JSON file (accumulating if file exists)
        json_path = self.to_json(product_data)
        print(f"\nParsed and combined {self.total_reviews_scraped} unique star-filtered reviews into {json_path}")
        return json_path


    def cleanup_files(self):
        """
        Delete the temporary files all_reviews.html and product_clean.json.
        Call this after processing to conserve disk space.
        """
        files_to_delete = ["all_reviews.html", "product_clean.json"]
        for filename in files_to_delete:
            file_path = os.path.join(self.output_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")

    def process(self):
        """
        Main method to run the complete review scraping and processing workflow:
        - Scrapes main review pages,
        - Parses and samples reviews by star rating,
        - Deduplicates and merges,
        - Serializes results to JSON,
        - Cleans up temporary files.
        """
        start_time = time.time()
        print("\n" + "="*50)
        print("PROCESS COMPLETE - SUMMARY")
        print("="*50)
        print(f"Pages processed: {self.scraping_success} successful, {self.scraping_failed} failed")
        print(f"Total reviews scraped: {self.total_reviews_scraped}")
        print(f"Total processing time: {time.time() - start_time:.2f} seconds")
        print(f"Results saved to: {self.output_dir}")
        print("="*50)

        self.cleanup_files()  # comment this line to keep the temporary files

if __name__ == "__main__":
    load_dotenv()
    SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
    AMAZON_COOKIES = os.getenv("AMAZON_COOKIES")
    PRODUCT_INFO = {
        "asin": "B0CZL2SLCJ",  # Example ASIN
        "price": "$299.99",
        "image_url": "https://example.com/image.jpg",
        "product_url": "https://www.amazon.com/dp/B0CZL2SLCJ"
    }
    PAGES_TO_SCRAPE = 5

    if not SCRAPINGBEE_API_KEY:
        print("Error: API_KEY not found in .env file")
        exit(1)
    if not AMAZON_COOKIES:
        print("Warning: AMAZON_COOKIES not found in .env file. May block scraping.")

    # Note: PRODUCT_INFO and PAGES_TO_SCRAPE can be customized as needed
    processor = AmazonReviewProcessor(SCRAPINGBEE_API_KEY, "hp", PRODUCT_INFO, PAGES_TO_SCRAPE)
    processor.process()
