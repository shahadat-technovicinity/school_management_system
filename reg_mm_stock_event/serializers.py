from rest_framework import serializers
from .models import StockInventory

class StockInventorySerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    category_location = serializers.ReadOnlyField(source='display_category')

    class Meta:
        model = StockInventory
        fields = '__all__'