from connect import mongo_connect, connect_rabbitmq
from models import Contacts
from faker import Faker
import json


fake = Faker()


def create_contacts(n, rabbitmq_channel, queue_name):
    for _ in range(n):
        contact = Contacts(fullname=fake.name(), email=fake.email())
        contact.save()
        print(f"Saved: {contact.fullname}, {contact.email}")

        message = json.dumps({"contact_id": str(contact.id)})
        rabbitmq_channel.basic_publish(
            exchange="", routing_key=queue_name, body=message
        )
        print(f"Sent to RabbitMQ: {message}")


if __name__ == "__main__":
    mongo_connect()

    # Виніс підключення брокера в модуль connect
    # credentials = pika.PlainCredentials("guest", "guest")
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host="127.0.0.1", port=5672, credentials=credentials)
    # )
    connection = connect_rabbitmq()
    channel = connection.channel()

    queue_name = "contacts_queue"
    channel.queue_declare(queue=queue_name)

    create_contacts(20, channel, queue_name)

    connection.close()
