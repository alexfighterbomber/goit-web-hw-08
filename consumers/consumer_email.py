import json
import time
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

# Підключення до RabbitMQ
def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()
    return connection, channel

def send_email_stub(email):
    """Фейкова функція відправки email."""
    print(f"Відправка email на {email}...")
    time.sleep(1)  # Імітация затримки
    print(f"Email на {email} відправлено!")

def process_message(ch, method, properties, body):
    """Обробляє повідомлення з черги."""
    data = json.loads(body)
    contact_id = data.get("contact_id")
    contact = Contact.objects(id=contact_id).first()

    if contact and not contact.sent:
        send_email_stub(contact.email)
        contact.sent = True
        contact.save()
        print(f"Контакт {contact.fullname} ({contact.email}) оновлено в БД.")

    ch.basic_ack(delivery_tag=method.delivery_tag)  # Підтвердження обробки повідомлення

def start_consumer():
    """Запускає consumer, для прослуховування черги RabbitMQ."""
    connection, channel = get_rabbitmq_connection()
    channel.queue_declare(queue="email_queue")
    
    channel.basic_consume(queue="email_queue", on_message_callback=process_message)
    print("Очікування повідоьлень. Для виходу натисніть CTRL+C")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Завершення роботи...")
        channel.stop_consuming()
        connection.close()

start_consumer()
