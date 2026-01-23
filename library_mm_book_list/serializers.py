from rest_framework import serializers
from .models import *

class Book_model_serializers(serializers.ModelSerializer):
    class Meta:
        model = Book_model
        fields = '__all__'