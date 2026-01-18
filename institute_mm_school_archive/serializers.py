from rest_framework import serializers
from .models import *

class SchoolArchiveDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = School_Archive_Document
        fields = '__all__'