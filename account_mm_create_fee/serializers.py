from rest_framework import serializers
from .models import CreateFee, FormFilupAmount
from django.db import models
from decimal import Decimal


class CreateFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateFee
        fields = '__all__'
        


class FormFilupAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFilupAmount
        fields = '__all__'