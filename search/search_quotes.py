import redis
from models.models import Author, Quote
from services.connect import *
from redis_lru import RedisLRU

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)
cache = RedisLRU(redis_client, max_size=1000)

@cache
def search_by_name(name_prefix):
    """Шукає цитати за ім'ям(частиною імені) автора."""
    author = Author.objects(fullname__istartswith=name_prefix).first()
    if not author:
        return []
    quotes = Quote.objects(author=author)
    result = [quote.quote for quote in quotes]
    return result

@cache
def search_by_tag(tag_prefix):
    """Шукає цитати за тегом /частиною тега."""
    quotes = Quote.objects(tags__istartswith=tag_prefix)
    result = [quote.quote for quote in quotes]
    return result

@cache
def search_by_tags(tags):
    """Шукає цитати за тегами."""
    tag_list = tags.split(",")
    quotes = Quote.objects(tags__in=tag_list)
    result = [quote.quote for quote in quotes]    
    return result


def main():
    """Основний цикл."""
    while True:
        command = input("Введіть команду (name:, tag:, tags:, exit): ").strip()
        
        if command == "exit":
            print("Вихід...")
            break
        not_found = "Цитати не знайдено."
        if command.startswith("name:"):
            results = search_by_name(command[5:].strip())
            print("\n".join(results) if results else not_found)
        
        elif command.startswith("tag:"):
            results = search_by_tag(command[4:].strip())
            print("\n".join(results) if results else not_found)

        elif command.startswith("tags:"):
            results = search_by_tags(command[5:].strip())
            print("\n".join(results) if results else not_found)

main()