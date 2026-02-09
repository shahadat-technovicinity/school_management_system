from rest_framework import serializers
from apps.academics.models import ClassSection

class ClassSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSection
        fields = "__all__"
