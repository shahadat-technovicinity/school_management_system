from apps.academics.models import AcademicYear
from rest_framework import serializers


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'