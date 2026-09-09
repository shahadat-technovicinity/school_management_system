from rest_framework import serializers

class AttendanceReportSerializer(serializers.Serializer):
    classname = serializers.IntegerField(required=False, help_text="Class ID")
    section = serializers.IntegerField(required=False, help_text="Section ID")
    date = serializers.DateField(required=False, help_text="Date in YYYY-MM-DD format")