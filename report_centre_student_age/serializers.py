from rest_framework import serializers

class StudentAgeDistributionSerializer(serializers.Serializer):
    academic_year = serializers.CharField(required=False)
    class_name = serializers.CharField(required=False)