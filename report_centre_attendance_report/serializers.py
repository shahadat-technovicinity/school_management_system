from rest_framework import serializers

class AttendanceReportSerializer(serializers.Serializer):
    class_section = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)