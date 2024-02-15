import scrapy
from turboaz.items import TurboazItem


class TurbospiderSpider(scrapy.Spider):
    # if you want to limit the amount of pages use custom settings and give it a value
    # it will NOT stop instantly
    # custom_settings = {"CLOSESPIDER_PAGECOUNT": 55, "CONCURRENT_REQUEST": 1}

    name = "turbospider"
    allowed_domains = ["turbo.az"]
    start_urls = ["https://turbo.az/autos?q%5Bmake%5D%5B%5D=3"]

    def parse(self, response):
        cars = response.css(
            ".page-content .products-container .tz-container:nth-child(5) .products .products-i"
        )

        for car in cars:
            relative_url = car.css("a.products-i__link").attrib["href"]
            yield response.follow(
                "https://turbo.az" + relative_url, callback=self.parse_car_page
            )

        ## Next Page
        next_page = response.css("nav.pagination span.next a::attr(href)").get()
        if next_page:
            yield response.follow("https://turbo.az" + next_page, callback=self.parse)

    def parse_car_page(self, response):
        table_columns = response.css(".product-properties__column")
        car_item = TurboazItem()
        car_item["url"] = response.url
        car_item["price"] = response.css(
            ".product-price__i.product-price__i--bold ::text"
        ).get()
        car_item["price_azn"] = ""  # will get a value in Pipeline
        car_item["price_eur"] = ""

        value = response.css(
            ".product-owner__info .product-owner__info-name ::text"
        ).get()
        if value is None:  # if sold by a dealer owner_name is dealer
            value = response.css(
                ".product-shop__owner-right .product-shop__owner-name ::text"
            ).get()
        car_item["owner_name"] = value

        car_item["owner_location"] = response.css(
            ".product-owner__info .product-owner__info-region ::text"
        ).get()
        car_item["car_id"] = response.css(".product-actions__id ::text").get()
        car_item["post_renewed"] = response.css(
            ".product-statistics__i-text ::text"
        ).get()
        car_item["description"] = response.css(
            ".product-description__content p ::text"
        ).extract()
        car_item["location"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_region']"
            "/following-sibling::span/text()"
        ).get()
        car_item["brand"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_make_id']"
            "/following-sibling::span/a/text()"
        ).get()
        car_item["model"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_model']"
            "/following-sibling::span/a/text()"
        ).get()
        car_item["release_date"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_reg_year']"
            "/following-sibling::span/a/text()"
        ).get()
        car_item["category"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_category']"
            "/following-sibling::span/text()"
        ).get()
        car_item["color"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_color']"
            "/following-sibling::span/text()"
        ).get()
        car_item["engine"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_engine_volume']"
            "/following-sibling::span/text()"
        ).get()
        car_item["mileage_km"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_mileage']"
            "/following-sibling::span/text()"
        ).get()
        car_item["transmission"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_transmission']"
            "/following-sibling::span/text()"
        ).get()
        car_item["gear"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_gear']"
            "/following-sibling::span/text()"
        ).get()
        car_item["is_new"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_new']"
            "/following-sibling::span/text()"
        ).get()
        car_item["seats_count"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_seats_count']"
            "/following-sibling::span/span/text()"
        ).get()
        car_item["condition"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_Vəziyyəti']"
            "/following-sibling::span/text()"
        ).get()
        car_item["which_market"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_market']"
            "/following-sibling::span/text()"
        ).get()
        car_item["prior_owners_count"] = table_columns.xpath(
            "//div[@class='product-properties__i']/label[@for='ad_prior_owners_count']"
            "/following-sibling::span/span/text()"
        ).get()

        yield car_item
