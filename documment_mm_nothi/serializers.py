from rest_framework import serializers
from .models import Nothi

class NothiListSerializer(serializers.ModelSerializer):
    """নথির লিস্ট পাওয়ার জন্য সিরিয়ালাইজার"""
    class Meta:
        model = Nothi
        fields = ['id', 'nothi_no', 'title', 'academic_year', 'description', 'created_at']