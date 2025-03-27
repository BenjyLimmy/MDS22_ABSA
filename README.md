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

# Laptop Recommender App

A Flutter web application for recommending laptops based on user preferences.

## Quick Start with Docker (Pulling and Running Image)

```bash
# Pull the image
docker pull benjylim/laptop-recommender:latest

# Run the container
docker run -p 8080:80 benjylim/laptop-recommender:latest

# Open http://localhost:8080 in your browser
# Ensure that the backend server is running
```

## Updating Docker image

```bash
docker stop <container_id>
docker rm <container_id>
```

```bash
docker pull benjylim/laptop-recommender:latest
```

```bash
docker run -p 8080:80 benjylim/laptop-recommender:latest
```