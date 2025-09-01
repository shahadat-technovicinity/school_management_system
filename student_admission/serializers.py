# admissions/serializers.py

from rest_framework import serializers
from .models import *

class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAdmission
        fields = '__all__'


# class StudentParentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Parent
#         fields = '__all__'



# class StudentContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Contact
#         fields = '__all__'



# class StudentAcademicSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AcademicBackground
#         fields = '__all__'



# class StudentAditionalInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdditionalInfo
#         fields = '__all__'




# class StudentAdmissionMainSerializer(serializers.Serializer):
#     """
#     Main Serializer
#     """
#     # all serializer
#     student_info = StudentInfoSerializer()
#     parent = StudentParentSerializer()
#     contact = StudentContactSerializer()
#     academic_background = StudentAcademicSerializer()
#     additional_info = StudentAditionalInfoSerializer()

#     def create(self, validated_data):
#         """
#         Single request all data create
#         """
#         with transaction.atomic():
#             student_info_data = validated_data.pop('student_info')
#             parent_data = validated_data.pop('parent')
#             contact_data = validated_data.pop('contact')
#             academic_data = validated_data.pop('academic_background')
#             additional_data = validated_data.pop('additional_info')

#             # StudentAdmission object create
#             student_admission = StudentAdmission.objects.create(**student_info_data)
            
#             # OneToOneField object create
#             Parent.objects.create(student_admission=student_admission, **parent_data)
#             Contact.objects.create(student_admission=student_admission, **contact_data)
#             AcademicBackground.objects.create(student_admission=student_admission, **academic_data)
#             AdditionalInfo.objects.create(student_admission=student_admission, **additional_data)

#             return student_admission

#     def update(self, instance, validated_data):

#         student_info_data = validated_data.pop('student_info', {})
#         parent_data = validated_data.pop('parent', {})
#         contact_data = validated_data.pop('contact', {})
#         academic_data = validated_data.pop('academic_background', {})
#         additional_data = validated_data.pop('additional_info', {})

#         for attr, value in student_info_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if parent_data:
#             for attr, value in parent_data.items():
#                 setattr(instance.parent, attr, value)
#             instance.parent.save()

#         if contact_data:
#             for attr, value in contact_data.items():
#                 setattr(instance.contact, attr, value)
#             instance.contact.save()
        
#         if academic_data:
#             for attr, value in academic_data.items():
#                 setattr(instance.academic_background, attr, value)
#             instance.academic_background.save()
        
#         if additional_data:
#             for attr, value in additional_data.items():
#                 setattr(instance.additional_info, attr, value)
#             instance.additional_info.save()

#         return instance

