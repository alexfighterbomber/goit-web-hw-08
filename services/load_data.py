import json
from models.models import Author, Quote
from services.connect import *

def load_authors():
    with open("data/authors.json", "r", encoding="utf-8") as f:
        authors_data = json.load(f)

    for data in authors_data:
        # Перевіряємо, чи є вже автор
        author = Author.objects(fullname=data["fullname"]).first()
        if not author:
            # Створюємо, якщо немає
            author = Author(
                fullname=data["fullname"],
                born_date=data["born_date"],
                born_location=data["born_location"],
                description=data["description"]
            )
            author.save()

def load_quotes():
    with open("data/qoutes.json", "r", encoding="utf-8") as f:
        quotes_data = json.load(f)

    for data in quotes_data:
        author = Author.objects(fullname=data["author"]).first()
        if author:
            # Перевіряємо, чи є вже такая цитата
            if not Quote.objects(quote=data["quote"]).first():
                Quote(
                    tags=data["tags"],
                    author=author,
                    quote=data["quote"]
                ).save()


load_authors()
load_quotes()
print("Дані завантажено успішно.")
