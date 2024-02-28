from models import Authors
from datetime import datetime
from connect import mongo_connect
import json

if __name__ == "__main__":
    mongo_connect()

    def parse_date(date_string):
        try:
            return datetime.strptime(date_string, "%B %d, %Y")
        except ValueError as e:
            print(f"Error parsing date: {e}")
            return None

    path_to_json = "../json_data/authors.json"
    with open(path_to_json, "r") as file:
        authors_data = json.load(file)

        for author_entry in authors_data:
            # Конвертація рядка дати у datetime об'єкт
            born_date = parse_date(author_entry.get("born_date", ""))

            # Створення та збереження об'єкту автора
            author = Authors(
                name=author_entry.get("fullname", ""),
                born_date=born_date,
                born_location=author_entry.get("born_location", ""),
                description=author_entry.get("description", ""),
            )
            author.save()
