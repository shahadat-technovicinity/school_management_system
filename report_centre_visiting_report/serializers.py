from rest_framework import serializers
from .models import VisitingReport


class VisitingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitingReport
        fields = '__all__'
        extra_kwargs = {
            'officer_name': {'required': False},
            'designation': {'required': False},
            'office': {'required': False},
            'visit_date': {'required': False},
        }