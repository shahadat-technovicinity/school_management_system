from rest_framework import serializers
from apps.students.models import Student, GuardianDetails, AdditionalDetails, StudentDiscipline
from apps.academics.models import Class, Section

class GuardianDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianDetails
        exclude = ('student',)

class AdditionalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetails
        exclude = ('student',)

class StudentDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDiscipline
        fields = '__all__'

class StudentManagementSerializer(serializers.ModelSerializer):
    guardian_info = GuardianDetailsSerializer(required=False)
    additional_info = AdditionalDetailsSerializer(required=False)
    disciplinary_records = StudentDisciplineSerializer(many=True, read_only=True)
    
    # Summary fields for UI display
    attendance_percentage = serializers.SerializerMethodField()
    disciplinary_status = serializers.SerializerMethodField()
    
    # Read-only labels for the UI grid/list
    class_label = serializers.CharField(source='class_name_static', read_only=True)
    section_label = serializers.CharField(source='section_static', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def get_attendance_percentage(self, obj):
        # Placeholder for real attendance calculation logic from attendance app
        return 85.5 

    def get_disciplinary_status(self, obj):
        if obj.disciplinary_records.filter(severity='high').exists():
            return "At Risk"
        return "Good Standing"

    def create(self, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        student = Student.objects.create(**validated_data)

        if guardian_data:
            GuardianDetails.objects.create(student=student, **guardian_data)
        if additional_data:
            AdditionalDetails.objects.create(student=student, **additional_data)

        return student

    def update(self, instance, validated_data):
        guardian_data = validated_data.pop('guardian_info', None)
        additional_data = validated_data.pop('additional_info', None)

        # Update core student fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create guardian info
        if guardian_data:
            guardian_obj, created = GuardianDetails.objects.get_or_create(student=instance)
            for attr, value in guardian_data.items():
                setattr(guardian_obj, attr, value)
            guardian_obj.save()

        # Update or create additional info
        if additional_data:
            additional_obj, created = AdditionalDetails.objects.get_or_create(student=instance)
            for attr, value in additional_data.items():
                setattr(additional_obj, attr, value)
            additional_obj.save()

        return instance
