# committees/serializers.py
from rest_framework import serializers
from .models import *

class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeMember
        fields = '__all__'
        ref_name = 'TeacherCommitteeMemberSerializer'
        read_only_fields = ['id', 'created_at']