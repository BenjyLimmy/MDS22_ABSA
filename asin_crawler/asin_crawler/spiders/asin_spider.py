import scrapy
from scrapy import Request

class AsinSpiderSpider(scrapy.Spider):
    name = "asin_spider"
    allowed_domains = ["amazon.com"]
    # Starting with the search query for "hp laptop"
    start_urls = ["https://www.amazon.com/s?k=hp+laptop"]

    def parse(self, response):
        # Loop over product containers; Amazon often uses divs with class "s-result-item" and a data-asin attribute.
        for product in response.css("div.s-result-item"):
            asin = product.attrib.get("data-asin")
            if asin:
                yield {"asin": asin}

        # Find and follow the "Next" page link (pagination)
        next_page = response.css("li.a-last a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield Request(next_page_url, callback=self.parse)