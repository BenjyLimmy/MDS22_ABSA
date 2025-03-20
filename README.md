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
- `MONGO_USERNAME`
- `MONGO_PASSWORD`

## Running the Scraper Pipeline

### To run the scraper pipeline:

- Just run the `run_scrape_pipeline.py` file.
- The pipeline will run the following in order:
  - ASIN Crawler
  - Review Scraper for each ASIN ID
  - Review Summariser
  - Sentiment Analysis
