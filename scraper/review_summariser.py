from openai_handler import OpenAIHandler
from dotenv import load_dotenv
import json
import os

load_dotenv()

SUMMARISATION_PROMPT = """
    You will be given a string of laptop product reviews. Each review is separated by a semicolon ";". Your task is to summarise the reviews and provide a summary of the reviews. Your summary must be concise and within **1 sentence**, start your summary with "The laptop ...". You do not need to mention the laptop model name in the summary. **Only** return the summary of the reviews.
"""

class ReviewSummariser:
    def run(self):
        path_to_product_json = './scraper_results/reviews.json'
        out_path = './scraper_results/processed_reviews.json'

        if not os.path.exists(path_to_product_json):
            print("No reviews file found. Make sure the reviews have been processed.")
            return

        with open(path_to_product_json, 'r') as f:
            reviews_data = json.load(f)

        if not reviews_data:
            print("No reviews found.")
            return

        # Process each laptop and add a summary
        for laptop in reviews_data:
            # Ensure there is a review key (using an empty list as a default)
            temp_review_str = "; ".join([txt.get("review_text") for txt in laptop.get("review", [])])
            client = OpenAIHandler(SUMMARISATION_PROMPT)
            summary = client.get_response(temp_review_str)
            print(f"\nSummary for {laptop.get('product_id')}: {summary}\n")
            laptop['review_summary'] = summary

        # Check if the results file exists; if so, load and append, otherwise start fresh
        if os.path.exists(out_path):
            with open(out_path, 'r') as f:
                existing_data = json.load(f)
            combined_data = existing_data + reviews_data
        else:
            combined_data = reviews_data

        with open(out_path, 'w') as f:
            json.dump(combined_data, f, indent=4)
            