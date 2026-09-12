from rest_framework import serializers

class ParentVoterListSerializer(serializers.Serializer):
    voter_number = serializers.CharField(help_text="4-digit formatted serial e.g. 0001")
    voter_name = serializers.CharField()
    student_name = serializers.CharField()
    student_class = serializers.CharField()
    class_roll = serializers.CharField()
    section_name = serializers.CharField()
    student_id = serializers.CharField()