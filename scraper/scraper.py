import requests
import os
import json
import re
import time
from bs4 import BeautifulSoup
from scrapy import Selector
from dotenv import load_dotenv

class AmazonReviewProcessor:
    def __init__(self, api_key, product_id, review_pages=5):
        self.api_key = api_key
        self.product_id = product_id
        self.pages = review_pages
        self.output_dir = "sample_data"
        self.ensure_output_dir()
        
        # Track for summary
        self.total_reviews_scraped = 0
        self.scraping_success = 0
        self.scraping_failed = 0

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

    def scrape_reviews(self):
        """Scrape reviews from Amazon using ScrapingBee"""
        print("Step 1: Scraping Amazon reviews...")

        # Create a BeautifulSoup object to hold the combined content
        combined_soup = BeautifulSoup('<html><head><title>Combined Amazon Reviews</title></head><body></body></html>', 'html.parser')
        body = combined_soup.find('body')
        
        
        for page_number in range(1, self.pages + 1):
            print(f"\nProcessing page {page_number}...")
            content = self.send_request(page_number)
            
            if content:
                # Add a page divider
                divider = combined_soup.new_tag('div')
                divider.attrs['style'] = 'margin: 20px 0; padding: 10px; background-color: #f0f0f0; border-top: 2px solid #ccc;'
                divider.string = f'--- Page {page_number} ---'
                body.append(divider)
                
                # Parse the content and extract the main content
                page_soup = BeautifulSoup(content, 'html.parser')
                
                # Get the main content (we'll add the whole page_soup to maintain structure)
                body.append(page_soup.body or page_soup)
                self.scraping_success += 1
            else:
                self.scraping_failed += 1
            
            # Add a small delay to avoid hitting rate limits
            if page_number < self.pages:
                time.sleep(2)
        
        # Save combined HTML content
        html_path = os.path.join(self.output_dir, "all_reviews.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(combined_soup))
        
        print(f"\nSaved combined HTML to {html_path}")
        return html_path
    
    def send_request(self, page_number):
        """Send request to ScrapingBee API"""
        base_url = f'https://www.amazon.com/dp/product-reviews/{self.product_id}/ref=cm_cr_dp_d_show_all_btm'
        url = f'{base_url}?ie=UTF8&reviewerType=all_reviews&pageNumber={page_number}'

        print(f"Scraping page {page_number} - {url}")   
        response = requests.get(
        url='https://app.scrapingbee.com/api/v1',
        params={
            'api_key': self.api_key,
            'url': url,
            'block_resources': 'false',
            'cookies': os.getenv("AMAZON_COOKIES", "")
        },
    )
        
        print(f'Page {page_number} - HTTP Status Code: {response.status_code}')
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to retrieve page {page_number}")
            return None

    def parse_reviews(self, html_path):
        """Parse reviews from HTML content"""
        print("\nStep 2: Parsing reviews from HTML...")

            # Read HTML from a file (e.g., "source.html")
        with open(html_path, "r", encoding="utf-8") as file:
            html = file.read()

        # Create a Selector instance using the HTML text
        sel = Selector(text=html)

        # --- Extract product details ---
        title = sel.css("h1.product-info-title a::text").get()
        average_rating = sel.css("i[data-hook='average-star-rating'] span.a-icon-alt::text").get()
        review_count = sel.css("div[data-hook='total-review-count'] span::text").get()

        # Extract histogram percentages from the aria-label attribute of each li
        histogram = {}
        for li in sel.css("ul#histogramTable li"):
            aria_label = li.css("a::attr(aria-label)").get()
            if aria_label:
                match = re.search(r"(\d+)\s+stars represent (\d+)%", aria_label)
                if match:
                    star = match.group(1)
                    percent = match.group(2) + "%"
                    histogram[f"{star}_star"] = percent

        # --- Extract reviews (if present) ---
        reviews = []

        # Extraction for main reviews (if the HTML contains such review items)
        main_reviews = sel.css("li[data-hook='review']")
        for review in main_reviews:
            review_id = review.attrib.get("id")
            reviewer = review.css("div.a-profile-content span.a-profile-name::text").get()
            rating = review.css("i[data-hook='review-star-rating'] span.a-icon-alt::text").get()
            title_parts = review.css("a[data-hook='review-title'] span::text").getall()
            review_title = ' '.join(part.strip() for part in title_parts if part.strip())
            review_date = review.css("span[data-hook='review-date']::text").get()
            body_parts = review.css("span[data-hook='review-body'] span::text").getall()
            review_text = ' '.join(part.strip() for part in body_parts if part.strip())
            
            reviews.append({
                "source": "main",
                "review_id": review_id,
                "reviewer": reviewer,
                "rating": rating,
                "review_title": review_title,
                "review_date": review_date,
                "review_text": review_text,
            })
        self.total_reviews_scraped = len(reviews)

        # --- Combine product details and reviews ---
        product_data = {
            "title": title,
            "product_id": self.product_id,
            "average_rating": average_rating,
            "review_count": review_count,
            "histogram": histogram,
            # Place the review list under the "review" attribute
            "review": reviews
        }

        # Append the product_data to product.json instead of overwriting it
        json_path = os.path.join(self.output_dir, "product.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as infile:
                try:
                    existing_data = json.load(infile)
                    # Ensure the existing data is a list
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(product_data)
        with open(json_path, "w", encoding="utf-8") as outfile:
            json.dump(existing_data, outfile, ensure_ascii=False, indent=4)

        print(f"Parsed {len(reviews)} reviews and appended to {json_path}")
        return json_path

    def process(self):
        """Main method to run the complete workflow"""
        start_time = time.time()
        
        # Step 1: Scrape reviews
        html_path = self.scrape_reviews()
        
        # Step 2: Parse reviews from HTML
        json_path = self.parse_reviews(html_path)
        
        # Print summary
        print("\n" + "="*50)
        print("PROCESS COMPLETE - SUMMARY")
        print("="*50)
        print(f"Pages processed: {self.scraping_success} successful, {self.scraping_failed} failed")
        print(f"Total reviews scraped: {self.total_reviews_scraped}")
        print(f"Total processing time: {time.time() - start_time:.2f} seconds")
        print(f"Results saved to: {self.output_dir}")
        print("="*50)

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration
    SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
    AMAZON_COOKIES = os.getenv("AMAZON_COOKIES")
    # Insert ASIN number of laptop
    PRODUCT_ID = "B0CZL2SLCJ"  # Eg: HP Stream 14 laptop
    PAGES_TO_SCRAPE = 5
    
    # Verify API key is loaded
    if not SCRAPINGBEE_API_KEY:
        print("Error: API_KEY not found in .env file")
        exit(1)
    if not AMAZON_COOKIES:
        print("Warning: AMAZON_COOKIES not found in .env file. May block scraping.")
        
    # Create processor and run workflow
    processor = AmazonReviewProcessor(SCRAPINGBEE_API_KEY, PRODUCT_ID, PAGES_TO_SCRAPE)
    processor.process()