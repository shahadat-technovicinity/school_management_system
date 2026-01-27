from rest_framework import serializers
from .models import *

class PicnicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picnic
        fields = '__all__'