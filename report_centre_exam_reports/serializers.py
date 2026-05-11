from rest_framework import serializers

class ExamReportSerializer(serializers.Serializer):
    exam_setup = serializers.IntegerField(required=False)
    class_name = serializers.IntegerField(required=False)
    student = serializers.IntegerField(required=False)