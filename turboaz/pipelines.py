# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

USD_TO_AZN = 1.7
AZN_TO_USD = 0.59


class TurboazPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        ## delete km from mileage and turn it to int
        mileage_km = adapter.get("mileage_km")
        index = mileage_km.find("km")
        mileage_str = mileage_km[:index].strip()
        adapter["mileage_km"] = int("".join(mileage_str.split()))

        ## remove text from data and turn it to int
        strip_colons = ("post_renewed", "announcement_num")
        for key in strip_colons:
            value = adapter.get(key)
            adapter[key] = value.split(":")[1]

        ## price assignment and turn it to int
        value = adapter.get("price")
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
        return item
