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
    # SlugRelatedField সরিয়ে PrimaryKeyRelatedField ব্যবহার করা হচ্ছে
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__name='Teacher')
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject_Name.objects.all()
    )

    class Meta:
        model = ClassRoutine
        fields = '__all__'

    # GET করার সময় ফ্রন্টএন্ড যেন ID এবং Name দুটোই দেখতে পায়
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.teacher:
            representation['teacher'] = {
                'id': instance.teacher.id,
                'name': getattr(instance.teacher, 'name', str(instance.teacher))
            }
            
        if instance.subject:
            representation['subject'] = {
                'id': instance.subject.id,
                'name': getattr(instance.subject, 'name', str(instance.subject))
            }
            
        return representation