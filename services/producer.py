import json
import faker
import random
import pika
from mongoengine import connect
import configparser
from models.contact import Contact


config = configparser.ConfigParser()
config.read('config/config.ini')

mongo_user = config.get('DB', 'user')
mongodb_pass = config.get('DB', 'pass')
db_name = "email_sender"
domain = config.get('DB', 'domain')

# Підключення до MongoDB
connect(host=f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority""", ssl=True)


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

# Создаем две очереди: для Email и SMS
channel.queue_declare(queue="email_queue")
channel.queue_declare(queue="sms_queue")

# Генерація фейкових контактів
fake = faker.Faker()

for _ in range(10):  # 10 контактів
    contact = Contact(
        fullname=fake.name(),
        email=fake.email(),
        phone_number=fake.phone_number(),
        preferred_contact=random.choice(["email", "sms"])
    )
    contact.save()
    
    # Отправляем в соответствующую очередь
    message = json.dumps({"contact_id": str(contact.id)})
    if contact.preferred_contact == "email":
        channel.basic_publish(exchange="", routing_key="email_queue", body=message)
    else:
        channel.basic_publish(exchange="", routing_key="sms_queue", body=message)

    print(f"Додано контакт: {contact.fullname}, метод зв'язку: {contact.preferred_contact}")

connection.close()