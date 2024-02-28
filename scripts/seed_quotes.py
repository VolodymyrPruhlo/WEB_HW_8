from connect import mongo_connect
from models import Quotes, Authors
import json

if __name__ == "__main__":
    mongo_connect()
    path_to_json = "../json_data/quotes.json"
    with open(path_to_json, "r") as file:
        quote_data = json.load(file)

        for quote_entry in quote_data:
            author_name = quote_entry.get("author")
            author = Authors.objects(name=author_name).first()
            if not author:
                author = Authors(name=author_name)
                author.save()

            quotes = Quotes(
                tags=quote_entry.get("tags"),
                author=author,
                quote=quote_entry.get("quote"),
            )
            quotes.save()
