from datetime import datetime

from mongoengine import Document
from mongoengine.fields import (
    DateTimeField,
    ListField,
    StringField,
    ReferenceField,
    BooleanField,
)


class Authors(Document):
    name = StringField()
    born_date = DateTimeField(default=datetime.now)
    born_location = StringField()
    description = StringField()


class Quotes(Document):
    tags = ListField()
    author = ReferenceField(Authors)
    quote = StringField()


class Contacts(Document):
    fullname = StringField()
    email = StringField()
    contacting = BooleanField(default=False)
