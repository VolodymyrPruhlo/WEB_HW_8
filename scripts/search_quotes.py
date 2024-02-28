from connect import mongo_connect, cache
from models import Quotes, Authors
from mongoengine.queryset.visitor import Q
import re
import json


def get_cached_result(key):
    result = cache.get(key)
    return json.loads(result) if result else None


def set_cached_result(key, value, expire_time=60 * 60):
    cache.set(key, json.dumps(value), ex=expire_time)


def get_cached_quotes_by_tags(tags):
    cache_key = "quotes_" + "_".join(sorted(tags))
    cached_result = cache.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    else:
        return None


def set_cached_quotes_by_tags(tags, quotes, expire_time=60 * 60):
    cache_key = "quotes_" + "_".join(sorted(tags))
    cached_result = json.dumps(quotes)
    cache.set(cache_key, cached_result, ex=expire_time)


def find_quotes_by_author(author_name):
    cache_key = f"author_quotes_{author_name.lower()}"

    cached_quotes = get_cached_result(cache_key)
    if cached_quotes is not None:
        return cached_quotes

    regex = re.compile(f"^{re.escape(author_name)}", re.IGNORECASE)
    author = Authors.objects(Q(name=regex)).only("id", "name").first()
    if not author:
        return []

    quotes = Quotes.objects(author=author.id).only("quote")
    if not quotes:
        return []

    results = [f"Quote by {author.name} - {q.quote}" for q in quotes]

    set_cached_result(cache_key, results)

    return results


def find_author_name_by_tag(tag):
    author_name = get_cached_result(f"author_name_{tag}")
    if author_name:
        return author_name

    quotes = Quotes.objects(tags__icontains=tag)
    for quote in quotes:
        author_id = quote.author.id
        author = Authors.objects(id=author_id).only("name").first()
        if author:
            set_cached_result(f"author_name_{tag}", author.name)
            return author.name
    return None


def find_quotes_by_tag(tag):
    cached_quotes = get_cached_result(f"quotes_{tag}")
    if cached_quotes:
        return cached_quotes

    author_name = find_author_name_by_tag(tag)
    if not author_name:
        return []

    quotes_with_tags = Quotes.objects(tags__icontains=tag).only("tags", "quote")
    result = [
        f"Quote by {author_name} - {quote.quote}"
        for quote in quotes_with_tags
        if tag in quote.tags
    ]

    set_cached_result(f"quotes_{tag}", result)

    return result


def find_quotes_by_tags(tags):
    # Спроба отримати цитати з кешу
    cached_quotes = get_cached_quotes_by_tags(tags)
    if cached_quotes is not None:
        return cached_quotes

    # Якщо цитат у кеші немає, знайти їх у базі даних
    quotes_with_tags = Quotes.objects(tags__in=tags).only("quote", "author")
    quotes_with_authors = []
    for quote in quotes_with_tags:
        author = Authors.objects(id=quote.author.id).only("name").first()
        if author:
            quotes_with_authors.append(f"Quote by {author.name} - {quote.quote}")

    # Кешувати результати перед поверненням
    set_cached_quotes_by_tags(tags, quotes_with_authors)

    return quotes_with_authors


def main():
    while True:
        command_input = input("Enter command: ").strip()
        if command_input.lower() == "exit":
            print("Exiting the script.")
            break

        try:
            command, value = command_input.split(":", 1)
            value = value

            if command == "name":
                results = find_quotes_by_author(value)
                for quote in results:
                    print(quote)

            elif command == "tag":
                results = find_quotes_by_tag(value)
                for result in results:
                    print(result)

            elif command == "tags":
                results = find_quotes_by_tags(value)
                for result in results:
                    print(result)

        except ValueError:
            print("Invalid command format. Please use 'command:value' format.")


if __name__ == "__main__":
    mongo_connect()
    main()
