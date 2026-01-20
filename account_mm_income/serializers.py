from rest_framework import serializers
from .models import *

class account_income_serializer(serializers.ModelSerializer):
    class Meta:
        model = account_Income
        fields = "__all__"
