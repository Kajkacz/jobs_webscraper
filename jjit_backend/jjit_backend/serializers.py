
from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Offer

class OfferSerializer(DocumentSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

