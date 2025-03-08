from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scraper.scraper import AmazonReviewProcessor
from asin_crawler.asin_crawler.spiders.asin_spider import AsinSpiderSpider

import os
import json

load_dotenv()

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
if not SCRAPINGBEE_API_KEY:
    print("Error: SCRAPINGBEE_API_KEY not found in .env file")
    exit(1)

def run_spider(brand="hp", max_asins=None):
    """
    Starts the Scrapy spider to crawl HP laptop ASINs from Amazon.
    """
    process = CrawlerProcess(settings={
        "FEEDS": {
            "asins.json": {
                "format": "json",
                "overwrite": True,
            },
        },
        "LOG_LEVEL": "INFO",   # can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    })
    process.crawl(AsinSpiderSpider, brand=brand, max_asins=max_asins)
    process.start() # blocks here until the crawl is finished


def process_asins(review_pages_per_asin=3):
    """
    Reads the ASINs from asins.json and processes them.
    """
    if not os.path.exists('asins.json'):
        print("No ASIN file found. Make sure the spider has scraped some ASINs.")
        return

    with open('asins.json', 'r') as f:
        asins_data = json.load(f)

    if not asins_data:
        print("No ASINs scraped.")
        return

    # Loop through each scraped ASIN and process it
    for entry in asins_data:
        product_id = entry.get('asin')
        if product_id:
            print(f"\n=== Processing product: {product_id} ===")
            # Here you can decide whether to process all ASINs or just one
            processor = AmazonReviewProcessor(
                api_key=SCRAPINGBEE_API_KEY, 
                product_id=product_id, 
                review_pages=review_pages_per_asin
            )
            processor.process()
        else:
            print("Encountered an entry without an ASIN.")


if __name__ == "__main__":
    print("=== Running ASIN spider ===")

    # scrape ASINs, define the brand (hp and lg for now) and number of ASINs to scrape 
    run_spider(brand="hp", max_asins=3)

    print("=== Processing ASINs ===")

    # scrape reviews for each ASIN, define the number of review pages to scrape
    process_asins(review_pages_per_asin=2)
    
    print("=== Workflow complete ===")

    