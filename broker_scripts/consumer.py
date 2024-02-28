from connect import mongo_connect
from models import Contacts
import pika
import json
import sys


def send_email_stub(contact):
    print(f"Sending email to {contact.email}")


def update_contact(contact_id):
    contact = Contacts.objects(id=contact_id).first()
    if contact:
        contact.contacting = True
        contact.save()
        print(f"Updated contact {contact.fullname} to contacting=True")
        return contact
    return None


def main():
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="127.0.0.1", port=5672, credentials=credentials)
    )
    channel = connection.channel()

    channel.queue_declare(queue="contacts_queue")

    def callback(ch, method, properties, body):
        print("Received message:", body)
        try:
            data = json.loads(body)
            contact_id = data.get("contact_id")
            if contact_id:
                contact = update_contact(contact_id)
                if contact:
                    send_email_stub(contact)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
        except Exception as e:
            print(f"Unexpected error: {e}")

    channel.basic_consume(
        queue="contacts_queue", on_message_callback=callback, auto_ack=True
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    mongo_connect()
    main()
    sys.exit(0)
