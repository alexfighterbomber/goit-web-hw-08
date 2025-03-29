from mongoengine import Document, StringField, BooleanField

class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True, unique=True)
    phone_number = StringField(required=True, unique=True)
    preferred_contact = StringField(choices=["email", "sms"], required=True)
    sent = BooleanField(default=False)  # False — лист ще не відправлено
