# MDS22_ABSA

### Create a Python `virtualenv`:
```
py -m venv venv
```

### Activate your `venv`:
```
.\venv\Scripts\activate
```

### Install from `requirements.txt`:
```
pip install -r requirements.txt
```

### In your `.env` file, define the following:
  - `SCRAPINGBEE_API_KEY`
  - `AMAZON_COOKIES`

### To run the scrapy crawler to get asin IDs:
  - `cd` into asin_crawler
  - Run the following:
    ```
    scrapy crawl asin_spider -o <YOUR_FILE_NAME>
    ```
