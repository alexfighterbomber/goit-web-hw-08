from mongoengine import Document, StringField, ReferenceField, ListField


class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()

class Quote(Document):
    tags = ListField(StringField(), required=True)
    author = ReferenceField(Author, required=True)
    quote = StringField(required=True)
