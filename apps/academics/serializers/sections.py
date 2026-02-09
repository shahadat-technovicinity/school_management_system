from rest_framework import serializers

from apps.academics.models import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"
