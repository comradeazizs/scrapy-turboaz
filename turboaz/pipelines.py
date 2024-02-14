# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
import psycopg

USD_TO_AZN = 1.7
AZN_TO_USD = 0.59


class TurboazPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        ## delete km from mileage and turn it to int
        value = adapter.get("mileage_km")
        index = value.find("km")
        mileage_str = value[:index].strip()
        adapter["mileage_km"] = int("".join(mileage_str.split()))

        ## remove text from data
        strip_colons = ("post_renewed", "car_id")
        for key in strip_colons:
            value = adapter.get(key)
            adapter[key] = value.split(":")[1]

        ## price assignment and turn it to int
        value = adapter.get("price")  # TODO EURO converter
        if "USD" in value:
            index = value.find("USD")
            value = int("".join(value[:index].strip().split()))

            adapter["price_azn"] = value * USD_TO_AZN
            adapter["price"] = value
        elif "AZN" in value:
            index = value.find("AZN")
            value = int("".join(value[:index].strip().split()))

            adapter["price_azn"] = value
            adapter["price"] = value * AZN_TO_USD

        ## change type from string to datetime
        value = adapter["post_renewed"]
        adapter["post_renewed"] = datetime.strptime(value, "%d.%m.%Y")

        value = adapter["release_date"]
        adapter["post_renewed"] = datetime.strptime(value, "%Y")

        ## change datatype to boolean

        ## change datatype to integer
        int_conversions = (
            "mileage_km",
            "seats_count",
            "prior_owners_count",
            "car_id",
        )
        for convertible in int_conversions:
            value = adapter[convertible]
            adapter[convertible] = int(value)

        return item


class SaveToPostgresPipeline:

    def __init__(self):
        ## Connection Details

        hostname = "localhost"
        username = "postgres"
        password = "postgres"  # your password
        database = "cars" # create a database

        ## Create/Connect to database
        self.connection = psycopg.connect(
            host=hostname, user=username, password=password, dbname=database
        )

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create books table if none exists
        with self.cur as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cars(
                car_id DECIMAL PRIMARY KEY,
                url VARCHAR(255),
                price DECIMAL,
                price_azn DECIMAL,
                owner_name VARCHAR(255),
                owner_location  VARCHAR(255),
                post_renewed date,
                description text,
                location VARCHAR(255),
                brand VARCHAR(255),
                model VARCHAR(255),
                release_date date,
                category VARCHAR(255),
                color VARCHAR(255),
                engine VARCHAR(255),
                mileage_km DECIMAL,
                transmission VARCHAR(255),
                gear VARCHAR(255),
                is_new BOOLEAN,
                seats_count DECIMAL,
                condition VARCHAR(255),
                which_market VARCHAR(255),
                prior_owners_count DECIMAL
                )
                """
            )

    def process_item(self, item, spider):

        ## Define insert statement
        with self.cur as cur:
            cur.execute(
                """
                insert into cars(
                car_id,
                url,
                price,
                price_azn,
                owner_name,
                owner_location,
                post_renewed,
                description,
                location,
                brand,
                model,
                release_date,
                category,
                color,
                engine,
                mileage_km,
                transmission,
                gear,
                is_new,
                seats_count,
                condition,
                which_market,
                prior_owners_count
                ) values (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    )""",
                (
                    item["car_id"],
                    item["url"],
                    item["price"],
                    item["price_azn"],
                    item["owner_name"],
                    item["owner_location"],
                    item["post_renewed"],
                    item["description"],
                    item["location"],
                    item["brand"],
                    item["model"],
                    item["release_date"],
                    item["category"],
                    item["color"],
                    item["engine"],
                    item["mileage_km"],
                    item["transmission"],
                    item["gear"],
                    item["is_new"],
                    item["seats_count"],
                    item["condition"],
                    item["which_market"],
                    item["prior_owners_count"],
                ),
            )

            ## Execute insert of data into database
            self.connection.commit()
        return item

    def close_spider(self, spider):

        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()
