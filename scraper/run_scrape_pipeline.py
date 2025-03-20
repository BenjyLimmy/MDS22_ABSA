from dotenv import load_dotenv
from asin_scraper import AsinHandler
from review_summariser import ReviewSummariser
from review_sentiment import SentimentGenerator
from review_scraper import AmazonReviewProcessor

import os
import json

load_dotenv()

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
if not SCRAPINGBEE_API_KEY:
    print("Error: SCRAPINGBEE_API_KEY not found in .env file")
    exit(1)


def scrape_asins(brand, max_asins=None):
    """
    Starts the scraper to crawl laptop ASINs from Amazon.
    """
    if not brand:
        raise ValueError("No laptop brand specified.")

    handler = AsinHandler(brand=brand, max_asins=max_asins)
    handler.run()


def scrape_reviews(review_pages_per_asin=3):
    """
    Reads the ASINs from asins.json and processes them.
    """
    path_to_asins = './scraper_results/asins.json'

    if not os.path.exists(path_to_asins):
        print("No ASIN file found. Make sure the spider has scraped some ASINs.")
        return

    with open(path_to_asins, 'r') as f:
        asins_data = json.load(f)

    if not asins_data:
        print("No ASINs scraped.")
        return

    # Loop through each scraped ASIN and process it
    for entry in asins_data:
        # product_id = entry.get('asin')
        if entry:
            print(f"\n=== Processing product: {entry.get("asin")} ===")
            # Here you can decide whether to process all ASINs or just one
            processor = AmazonReviewProcessor(
                api_key=SCRAPINGBEE_API_KEY, 
                product_info=entry, 
                review_pages=review_pages_per_asin
            )
            processor.process()
        else:
            print("Encountered an entry without an ASIN.")


def add_summaries():
    """
    Adds summaries to the processed reviews and appends them to the results file.
    """
    summariser = ReviewSummariser()
    summariser.run()


def add_sentiments():
    """
    Adds sentiment analysis to the processed reviews and appends them to the results file.
    """
    sentiment_generator = SentimentGenerator()
    sentiment_generator.run()


if __name__ == "__main__":
    print("=== Running ASIN spider ===")

    # scrape ASINs, define the brand and number of ASINs to scrape 
    # refer to brand_filter_map in asin_spider.py for available brands, or below:
    # brand_filter_map = {
    #     "hp": ("hp", "&rh=n%3A21512780011%2Cp_123%3A308445"),
    #     "dell": ("dell", "&rh=n%3A21512780011%2Cp_123%3A241862"),
    #     "lenovo": ("lenovo", "&rh=n%3A21512780011%2Cp_123%3A391242"),
    #     "apple": ("apple", "&rh=n%3A21512780011%2Cp_123%3A110955"),
    #     "lg": ("lg", "&rh=n%3A21512780011%2Cp_123%3A46658"),
    # }

    # for brand in brand_filter_map.keys():
    # scrape_asins(brand="hp", max_asins=3)

    print("=== Processing ASINs ===")
    scrape_reviews(review_pages_per_asin=1)

    print("=== Adding summaries ===")
    # add_summaries()

    print("=== Adding sentiments ===")
    add_sentiments()

        # print("=== Workflow complete ===")
