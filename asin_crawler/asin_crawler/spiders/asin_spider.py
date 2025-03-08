import scrapy
from scrapy import Request

class AsinSpiderSpider(scrapy.Spider):
    name = "asin_spider"
    allowed_domains = ["amazon.com"]
    
    # Map of brands to their search keyword and filter_id
    brand_filter_map = {
        "hp": ("hp", "&rh=n%3A21512780011%2Cp_123%3A308445"),
        "dell": ("dell", "&rh=n%3A21512780011%2Cp_123%3A241862"),
        "lenovo": ("lenovo", "&rh=n%3A21512780011%2Cp_123%3A391242"),
        "apple": ("apple", "&rh=n%3A21512780011%2Cp_123%3A110955"),
        "lg": ("lg", "&rh=n%3A21512780011%2Cp_123%3A46658"),
    }

    def __init__(self, brand="hp", max_asins=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if brand not in self.brand_filter_map:
            self.logger.error(f"Brand '{brand}' not found. Defaulting to 'hp'.")
            brand = "hp"

        # extract brand value and filter_id from the brand_filter_map
        brand_value, filter_id = self.brand_filter_map[brand]
        self.start_urls = [f"https://www.amazon.com/s?k={brand_value}+laptop{filter_id}"]
        print(f"Starting URL: {self.start_urls[0]}")

        self.max_asins = int(max_asins) if max_asins is not None else None
        self.asin_count = 0

    def parse(self, response):
        # Loop over product containers and extract ASINs
        for product in response.css('div[role="listitem"][data-component-type="s-search-result"]'):
            # print(product)
            asin = product.attrib.get("data-asin")
            if asin:
                print(f"Found ASIN: {asin}")
                yield {"asin": asin}
                self.asin_count += 1

                # check if we reached the maximum number of ASINs
                if self.max_asins and self.asin_count >= self.max_asins:
                    self.logger.info(f"Reached the maximum number of ASINs: {self.max_asins}")
                    self.crawler.engine.close_spider(self, "max_asins_reached")
                    return

        # going to the next page if available and not reached the maximum number of ASINs
        next_page = response.css("li.a-last a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            print(f"Following pagination link: {next_page_url}")
            yield Request(next_page_url, callback=self.parse)