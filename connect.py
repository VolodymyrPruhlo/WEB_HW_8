from mongoengine import connect
import configparser
import os
import redis


cache = redis.Redis(host="localhost", port=6379, db=0)


def mongo_connect():
    config = configparser.ConfigParser()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.ini")
    config.read(config_path)

    mongo_user = config.get("DB", "user")
    mongo_pass = config.get("DB", "pass")
    db_name = config.get("DB", "db_name")
    domain = config.get("DB", "domain")

    connect(
        host=f"""mongodb+srv://{mongo_user}:{mongo_pass}@{domain}/{db_name}?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true"""
    )
