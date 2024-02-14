# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TurboazItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Fileclass BookItem(scrapy.Item):
    url = scrapy.Field()
    price = scrapy.Field()
    price_azn = scrapy.Field()
    owner_name = scrapy.Field()
    owner_location = scrapy.Field()
    car_id = scrapy.Field()
    post_renewed = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    release_date = scrapy.Field()
    category = scrapy.Field()
    color = scrapy.Field()
    engine = scrapy.Field()
    mileage_km = scrapy.Field()
    transmission = scrapy.Field()
    gear = scrapy.Field()
    is_new = scrapy.Field()
    seats_count = scrapy.Field()
    condition = scrapy.Field()
    which_market = scrapy.Field()
    prior_owners_count = scrapy.Field()
