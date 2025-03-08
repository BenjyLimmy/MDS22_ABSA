# MDS22_ABSA

FYP - ABSA on Laptop Reviews

## Setting Up Your Environment

### Create a Python `virtualenv`:

```
py -m venv venv
```

### Activate your `venv`:

```
.\venv\Scripts\activate
```

### Install packages from `requirements.txt`:

```
pip install -r requirements.txt
```

### In your `.env` file, define the following:

- `SCRAPINGBEE_API_KEY`
- `AMAZON_COOKIES`

## Running the Scraper Pipeline

### To run the scraper pipeline:

- Run the following:
  ```
  py -m scraper.run_scrape_pipeline
  ```
- The pipeline will run the following in order:
  - ASIN Crawler
  - Review Scraper for each ASIN ID

## Running the Crawler (Deprecated)

### To run the scrapy crawler to get asin IDs:

- `cd` into asin_crawler
- Run the following:
  ```
  scrapy crawl asin_spider -o <YOUR_FILE_NAME>.json
  ```
