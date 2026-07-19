# class_routine/serializers.py

from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from academic_create_subject.models import Subject_Name


User = get_user_model()

class TeacherListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)
    value = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["value", "label"]


class ClassRoutineSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(
        queryset=User.objects.filter(role__name='Teacher'),
        slug_field='name'
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject_Name.objects.all()
    )

    class Meta:
        model = ClassRoutine
        fields = '__all__'