from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from llm.openai_handler import OpenAIHandler
from scraper.scraper import AmazonReviewProcessor
from asin_crawler.asin_crawler.spiders.asin_spider import AsinSpiderSpider

import os
import json

load_dotenv()

SUMMARISATION_PROMPT = """
You will be given a string of laptop product reviews. Each review is separated by a semicolon ";". Your task is to summarise the reviews and provide a summary of the reviews. Your summary must be concise and within **1 sentence**, start your summary with "The laptop ...". **Only** return the summary of the reviews.
"""


SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
if not SCRAPINGBEE_API_KEY:
    print("Error: SCRAPINGBEE_API_KEY not found in .env file")
    exit(1)

def run_spider(brand, max_asins=None):
    """
    Starts the Scrapy spider to crawl HP laptop ASINs from Amazon.
    """
    if not brand:
        raise ValueError("No laptop brand specified.")

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
    Adds summaries to the processed reviews.
    """
    path_to_product_json = '/Users/danielkoh4971/Desktop/MDS22_ABSA/sample_data/product.json'
    out_path = '/Users/danielkoh4971/Desktop/MDS22_ABSA/sample_data/reviews_with_summaries.json'

    if not os.path.exists(path_to_product_json):
        print("No reviews file found. Make sure the reviews have been processed.")
        return

    with open(path_to_product_json, 'r') as f:
        reviews_data = json.load(f)

    if not reviews_data:
        print("No reviews found.")
        return

    for laptop in reviews_data:
        temp_review_str = "; ".join([txt.get("review_text") for txt in laptop.get("review")])
        client = OpenAIHandler(SUMMARISATION_PROMPT)
        summary = client.get_response(temp_review_str)
        print(f"\nSummary for {laptop.get('product_id')}: {summary}\n")
        laptop['review_summary'] = summary

    with open(out_path, 'w') as f:
        json.dump(reviews_data, f, indent=4)


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
    run_spider(brand="dell", max_asins=3) # TODO: 3 asins per brand for testing, 10 reviews per asin, round the percentage to nearest 10 and scrape # reviews based on the percentage

    print("=== Processing ASINs ===")

    # scrape reviews for each ASIN, define the number of review pages to scrape
    # 1 page = 10 reviews
    process_asins(review_pages_per_asin=1)

    print("=== Adding summaries ===")
    add_summaries()

    print("=== Workflow complete ===")
