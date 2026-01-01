# class_routine/serializers.py

from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model


##### Teacher Serializers
User = get_user_model()
class TeacherListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)
    value = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["value", "label"]
        ref_name = "ClassRoutineTeacherList"




######### Routine Serializer
class ClassRoutineSerializer(serializers.ModelSerializer):
    # teacher_detail = TeacherListSerializer(source='teacher', read_only=True)
    # teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    teacher = serializers.SlugRelatedField(
        queryset=User.objects.filter(role='Teacher'),
        slug_field='name' # এখানে 'name' ফিল্ড থেকে ডেটা নেওয়া হয়েছে
    )
    class Meta:
        model = ClassRoutine
        fields = '__all__'  
        # read_only_fields = ('teacher',) 


