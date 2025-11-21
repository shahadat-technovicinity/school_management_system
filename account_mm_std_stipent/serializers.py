# exam / serializers.py
from rest_framework import serializers
from .models import *

class stipend_stu_serializer(serializers.ModelSerializer):
    class Meta:
        model = stipend_student
        fields = "__all__"



class stipend_free_hf_serializer(serializers.ModelSerializer):
    class Meta:
        model = stipend_free_hf
        fields = "__all__"