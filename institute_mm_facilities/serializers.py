from rest_framework import serializers
from .models import FacilityFurnitureItem, FacilityLocation


class FacilityLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityLocation
        fields = '__all__'


class FacilityFurnitureSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='stock_item.item_name', read_only=True)
    item_type = serializers.CharField(source='stock_item.category', read_only=True)

    class Meta:
        model = FacilityFurnitureItem
        fields = '__all__'

    def validate(self, attrs):
        stock_item = attrs.get('stock_item')
        quantity = attrs.get('quantity', 0)

        if stock_item and quantity > stock_item.quantity:
            raise serializers.ValidationError(
                {"quantity": f"Reported quantity ({quantity}) cannot exceed total stock quantity ({stock_item.quantity})!"}
            )
        return attrs