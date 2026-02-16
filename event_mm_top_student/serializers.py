from rest_framework import serializers
from .models import *

class Top_StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Top_Student
        fields = '__all__'