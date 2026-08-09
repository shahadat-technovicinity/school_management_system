from rest_framework import serializers
from django.contrib.auth import get_user_model
from academic_create_subject.models import Subject_Name
from .models import Teacher

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "username", "role", "phone_number", "is_active"]
        read_only_fields = ["id", "is_active"]


class TeacherListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id", "user", "full_name", "gender", "subject", "subject_name",
            "class_assigned", "primary_contact_number", "status",
            "date_of_joining", "photo", "created_at",
        ]
        ref_name = "TeacherProfileList"


class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id", "user", "full_name", "email",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "mother_name",
            "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "permanent_address", "current_address", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeacherCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        help_text="ID of the existing user (role='Teacher') to link this teacher profile to"
    )
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    basic_salary = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False, allow_null=True
    )
    facebook = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    instagram = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    linkedin = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    youtube = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    twitter = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Teacher
        fields = [
            "user_id", "id",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "mother_name",
            "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "permanent_address", "current_address", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_user_id(self, user):
        if user.role.name.lower() != 'teacher':
            raise serializers.ValidationError(
                "Selected user must have role='Teacher'."
            )
        try:
            _ = user.teacher_profile
            raise serializers.ValidationError(
                "This user already has a teacher profile."
            )
        except Teacher.DoesNotExist:
            pass
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserMinimalSerializer(instance.user).data if instance.user else None
        return rep


class TeacherUpdateSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    basic_salary = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        required=False, allow_null=True
    )
    facebook = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    instagram = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    linkedin = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    youtube = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    twitter = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Teacher
        fields = [
            "user", "id",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "mother_name",
            "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "permanent_address", "current_address", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]