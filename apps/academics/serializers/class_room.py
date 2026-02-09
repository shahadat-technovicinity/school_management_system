from rest_framework import serializers
from apps.academics.models import Class
from apps.academics.serializers.academic_years import AcademicYearSerializer    

class ClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = "__all__"

    