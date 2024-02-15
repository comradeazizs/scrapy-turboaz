# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
import psycopg2

USD_TO_AZN, USD_TO_EUR = 1.7, 0.93
AZN_TO_EUR, AZN_TO_USD = 0.55, 0.59
EUR_TO_USD, EUR_TO_AZN = 1.07, 1.82


class TurboazPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## some queries return description as a list; unite the list of strings
        adapter["description"] = "".join(adapter["description"])

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if value is not None:
                adapter[field_name] = value.strip()

        ## get distance number from mileage and turn it to int
        value = adapter.get("mileage_km")
        index = value.find("km")
        distance = value[:index].strip()
        adapter["mileage_km"] = int("".join(distance.split()))

        ## remove text from data
        strip_colons = ("post_renewed", "car_id")
        for key in strip_colons:
            value = adapter.get(key)
            adapter[key] = value.split(":")[1]

        ## price assignment and turn it to int
        value = adapter.get("price").upper()
        if "USD" in value:
            index = value.find("USD")
            value = int("".join(value[:index].strip().split()))

            adapter["price"] = value  # USD value
            adapter["price_eur"] = value * USD_TO_EUR
            adapter["price_azn"] = value * USD_TO_AZN
        elif "AZN" in value:
            index = value.find("AZN")
            value = int("".join(value[:index].strip().split()))

            adapter["price"] = value * AZN_TO_USD
            adapter["price_eur"] = value * AZN_TO_EUR
            adapter["price_azn"] = value
        elif "EUR" in value:
            index = value.find("EUR")
            value = int("".join(value[:index].strip().split()))

            adapter["price"] = value * EUR_TO_USD
            adapter["price_eur"] = value
            adapter["price_azn"] = value * EUR_TO_AZN

        ## if sold by dealer owner_location is car location
        if adapter["owner_location"] is None:
            adapter["owner_location"] = adapter["location"]

        ## change type from string to datetime
        value = adapter["post_renewed"].strip()
        adapter["post_renewed"] = datetime.strptime(value, "%d.%m.%Y")

        value = adapter["release_date"].strip()
        adapter["release_date"] = datetime.strptime(value, "%Y")

        ## change datatype to boolean
        value = adapter["is_new"].lower()
        if value == "bəli":
            adapter["is_new"] = True
        elif value == "xeyr":
            adapter["is_new"] = False
        else:
            adapter["is_new"] = None

        ## change datatype to integer
        int_conversions = (
            "mileage_km",
            "seats_count",
            "prior_owners_count",
            "car_id",
            "price",  # multiplication can turn value to float; this will fix it
            "price_eur",
            "price_azn",
        )
        for convertible in int_conversions:
            value = adapter[convertible]
            if value is not None:
                adapter[convertible] = int(value)

        return item


class SaveToPostgresPipeline:

    def __init__(self):
        ## Connection Details

        hostname = "localhost"
        username = "postgres"
        password = "postgres"  # your password
        database = "cars"  # name of your previously created database

        ## Connect to database
        self.connection = psycopg2.connect(
            host=hostname, user=username, password=password, dbname=database
        )

        ## it will create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## it will create a cars table if it does not exist
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cars(
            car_id serial PRIMARY KEY,
            url VARCHAR(255),
            price DECIMAL,
            price_azn DECIMAL,
            price_eur DECIMAL,
            owner_name VARCHAR(255),
            owner_location  VARCHAR(255),
            post_renewed date,
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
            prior_owners_count DECIMAL,
            description text
            )
            """
        )

    def process_item(self, item, spider):

        ## Define insert statement
        try:
            self.cur.execute(
                """
                insert into cars(
                car_id,
                url,
                price,
                price_azn,
                price_eur,
                owner_name,
                owner_location,
                post_renewed,
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
                prior_owners_count,
                description
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
                    %s
                    )""",
                (
                    item["car_id"],
                    item["url"],
                    item["price"],
                    item["price_azn"],
                    item["price_eur"],
                    item["owner_name"],
                    item["owner_location"],
                    item["post_renewed"],
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
                    item["description"],
                ),
            )

            ## Execute insert of data into database
            self.connection.commit()
        except Exception as e:
            print(f"Error: {e}")
            self.connection.rollback()
        return item

    def close_spider(self, spider):

        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()
