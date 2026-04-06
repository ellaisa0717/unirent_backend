from rest_framework import serializers
from .models import Item, RentalTransaction

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalTransaction
        fields = '__all__'