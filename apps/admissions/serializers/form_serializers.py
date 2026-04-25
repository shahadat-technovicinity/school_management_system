from rest_framework import serializers
from student_admission.models import StudentAdmission
from apps.admissions.models import PreviousAcademicRecord, AdmissionSkill, AdmissionSkillLink

class PreviousAcademicRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousAcademicRecord
        exclude = ('admission',)

class StudentAdmissionSerializer(serializers.ModelSerializer):
    previous_academic_record = PreviousAcademicRecordSerializer(required=False)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    skill_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentAdmission
        fields = '__all__'
        read_only_fields = ('application_number', 'admin_form_number', 'admission_status', 'payment_status')

    def get_skill_names(self, obj):
        return [link.skill.name for link in obj.skills.all()]

    def create(self, validated_data):
        # Extract nested relations
        academic_data = validated_data.pop('previous_academic_record', None)
        skills_data = validated_data.pop('skills', [])

        # 1. Create the main Admission
        admission = StudentAdmission.objects.create(**validated_data)

        # Generate Application Number safely
        admission.application_number = f"APP-2025-{admission.id:04d}"
        admission.save()

        # 2. Create Previous Academic Record
        if academic_data:
            PreviousAcademicRecord.objects.create(admission=admission, **academic_data)

        # 3. Create/Link Skills
        for skill_name in skills_data:
            skill_obj, created = AdmissionSkill.objects.get_or_create(name=skill_name.strip())
            AdmissionSkillLink.objects.create(admission=admission, skill=skill_obj)

        return admission

    def update(self, instance, validated_data):
        academic_data = validated_data.pop('previous_academic_record', None)
        skills_data = validated_data.pop('skills', None)

        # Update main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update academic data
        if academic_data is not None:
            if hasattr(instance, 'previous_academic_record'):
                for attr, val in academic_data.items():
                    setattr(instance.previous_academic_record, attr, val)
                instance.previous_academic_record.save()
            else:
                PreviousAcademicRecord.objects.create(admission=instance, **academic_data)

        # Update skills
        if skills_data is not None:
            instance.skills.all().delete()
            for skill_name in skills_data:
                skill_obj, created = AdmissionSkill.objects.get_or_create(name=skill_name.strip())
                AdmissionSkillLink.objects.create(admission=instance, skill=skill_obj)

        return instance