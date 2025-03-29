import redis
import json
from models.models import Author, Quote
from services.connect import *

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

def get_cached_data(key):
    """Отримуємо дані з Redis."""
    cached_result = redis_client.get(key)
    if cached_result:
        return json.loads(cached_result)  # Декодуємо JSON в Python-об'єкт
    return None

def set_cached_data(key, data, expiration=900):
    """Зберігає дані в Redis на 15 хв."""
    redis_client.set(key, json.dumps(data), ex=expiration)

def search_by_name(name_prefix):
    """Шукає цитати за ім'ям(частиною імені) автора."""
    key = f"name:{name_prefix.lower()}"
    cached_result = get_cached_data(key)
    
    if cached_result:
        return cached_result

    author = Author.objects(fullname__istartswith=name_prefix).first()
    if not author:
        return []

    quotes = Quote.objects(author=author)
    result = [quote.quote for quote in quotes]

    set_cached_data(key, result)
    return result

def search_by_tag(tag_prefix):
    """Шукає цитати за тегом /частиною тега."""
    key = f"tag:{tag_prefix.lower()}"
    cached_result = get_cached_data(key)

    if cached_result:
        return cached_result

    quotes = Quote.objects(tags__istartswith=tag_prefix)
    result = [quote.quote for quote in quotes]

    set_cached_data(key, result)
    return result

def search_by_tags(tags):
    key = f"tags:{tags.lower()}"
    cached_result = get_cached_data(key)

    if cached_result:
        return cached_result

    tag_list = tags.split(",")
    quotes = Quote.objects(tags__in=tag_list)
    result = [quote.quote for quote in quotes]    

    set_cached_data(key, result)
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