# MDS22_ABSA

### In your `.env` file, define the following:
  - `SCRAPINGBEE_API_KEY`
  - `AMAZON_COOKIES`

### To run the scrapy crawler to get asin IDs:
  - `cd` into asin_crawler
  - Run the following:
    ```
    scrapy crawl asin_spider -o <YOUR_FILE_NAME>
    ```
