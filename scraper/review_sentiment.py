from openai_handler import OpenAIHandler
from dotenv import load_dotenv
import json
import os

load_dotenv()

SENTIMENT_PROMPT = """
    You are an aspect-based sentiment analysis engine. You will be given a JSON array of laptop reviews. Each review object contains at least a "star_rating" (for example, "5.0 out of 5 stars") and a "review_text". Your task is to analyze each review and extract aspect terms from the review text based on its sentiment. Only use the following allowed aspect terms:

   AUDIO, BATTERY, BUILD_QUALITY, DESIGN, DISPLAY, PERFORMANCE, PORTABILITY, PRICE

    For each review, if the review is positive (indicated by its star rating), extract the positive aspect terms mentioned in the review that match the allowed list. If the review is negative, extract the negative aspect terms. Some reviews may contain mixed sentiments; in that case, only include aspect terms clearly expressed with a positive sentiment in the positive list and vice versa.

    After processing all reviews, aggregate the results per star rating into a JSON object with the following keys:
    - "pos_5_aspects": list of unique positive aspect terms extracted from 5-star reviews.
    - "neg_5_aspects": list of unique negative aspect terms extracted from 5-star reviews.
    - "pos_4_aspects": list of unique positive aspect terms from 4-star reviews.
    - "neg_4_aspects": list of unique negative aspect terms from 4-star reviews.
    - "pos_3_aspects": list of unique positive aspect terms from 3-star reviews.
    - "neg_3_aspects": list of unique negative aspect terms from 3-star reviews.
    - "pos_2_aspects": list of unique positive aspect terms from 2-star reviews.
    - "neg_2_aspects": list of unique negative aspect terms from 2-star reviews.
    - "pos_1_aspects": list of unique positive aspect terms from 1-star reviews.
    - "neg_1_aspects": list of unique negative aspect terms from 1-star reviews.

    Return only the JSON object containing these keys and their corresponding arrays. If no aspect terms are found for a particular key, output an empty list for that key. **Do not** include any additional commentary or explanations.
"""

class SentimentGenerator:
    def run(self):
        path_to_product_json = './scraper_results/processed_reviews.json'
        out_path = './scraper_results/sentiment_analysis.json'

        if not os.path.exists(path_to_product_json):
            print("No processed reviews file found. Make sure the reviews have been processed.")
            return

        with open(path_to_product_json, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)

        if not reviews_data:
            print("No reviews found.")
            return

        # Process each laptop individually
        for laptop in reviews_data:
            # Initialize the aggregated sentiments dictionary for this laptop
            aggregated_sentiments = {
                "pos_5_aspects": [],
                "neg_5_aspects": [],
                "pos_4_aspects": [],
                "neg_4_aspects": [],
                "pos_3_aspects": [],
                "neg_3_aspects": [],
                "pos_2_aspects": [],
                "neg_2_aspects": [],
                "pos_1_aspects": [],
                "neg_1_aspects": []
            }
            
            for review in laptop.get("review", []):
                star_rating = review.get("star_rating", "")
                review_text = review.get("review_text", "")
                if star_rating and review_text:
                    # Prepare the JSON array as the prompt input
                    review_input = json.dumps([{
                        "star_rating": star_rating,
                        "review_text": review_text
                    }])
                    # Initialize and call your OpenAI client
                    client = OpenAIHandler(SENTIMENT_PROMPT)
                    response = client.get_response(review_input)
                    
                    try:
                        response_json = json.loads(response)
                    except json.JSONDecodeError:
                        print("Failed to decode JSON response from OpenAI for this review.")
                        continue
                    
                    # Merge each key's list from the response into aggregated_sentiments
                    for key in aggregated_sentiments:
                        new_aspects = response_json.get(key, [])
                        aggregated_sentiments[key].extend(new_aspects)
            
            # Remove duplicates for each sentiment key
            for key in aggregated_sentiments:
                aggregated_sentiments[key] = list(set(aggregated_sentiments[key]))
            
            # Append the aggregated sentiments to the current laptop dict under "review_sentiments"
            laptop["review_sentiments"] = aggregated_sentiments

        # Save the updated laptop data back to the output file
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(reviews_data, f, indent=4)

        print(f"Sentiment analysis complete. Results saved to {out_path}")

if __name__ == "__main__":
    sentiment_generator = SentimentGenerator()
    sentiment_generator.run()
    