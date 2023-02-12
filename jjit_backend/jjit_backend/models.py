
from mongoengine import Document, fields

class Offer(Document):
    title = fields.StringField()
