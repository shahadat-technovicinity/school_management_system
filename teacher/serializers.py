from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Teacher

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for nested representation.
    Excludes password and sensitive fields.
    """

    class Meta:
        model = User
        fields = ["id", "name", "username", "role", "phone_number", "is_active"]
        read_only_fields = ["id", "is_active"]


class TeacherListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing teachers with minimal fields.
    Used for GET /teachers/ endpoint.
    """
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "user",
            "teacher_id",
            "full_name",
            "gender",
            "subject",
            "class_assigned",
            "primary_contact_number",
            "status",
            "date_of_joining",
            "photo",
            "created_at",
        ]
        ref_name = "TeacherProfileList"


class TeacherDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for teacher detail view with all fields.
    Used for GET /teachers/{id}/ endpoint.
    """
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = Teacher
        fields = [
            # Identity
            "id",
            "user",
            "teacher_id",
            "full_name",
            "email",
            
            # Personal Info
            "gender",
            "date_of_birth",
            "marital_status",
            "languages_known",
            "class_assigned",
            "subject",
            "blood_group",
            "primary_contact_number",
            "father_name",
            "mother_name",
            "qualification",
            "work_experience",
            
            # Previous Employment
            "previous_school_name",
            "previous_school_address",
            "previous_school_phone",
            
            # Address
            "permanent_address",
            "current_address",
            
            # Identification
            "pan_number",
            
            # Payroll
            "epf_no",
            "basic_salary",
            "contract_type",
            "work_shift",
            "work_location",
            "date_of_joining",
            "date_of_leaving",
            
            # Leaves
            "medical_leaves",
            "casual_leaves",
            "maternity_leaves",
            "sick_leaves",
            
            # Bank Details
            "account_name",
            "account_number",
            "bank_name",
            "branch_name",
            "ifsc_code",
            
            # Transport
            "route_id",
            "vehicle_number",
            "pickup_point",
            
            # Hostel
            "hostel_id",
            "room_no",
            
            # Social Media
            "facebook",
            "instagram",
            "linkedin",
            "youtube",
            "twitter",
            
            # Documents
            "photo",
            "resume",
            "joining_letter",
            
            # Additional
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeacherCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a teacher profile.
    Used for POST /teachers/ endpoint.
    Links teacher to an existing user.
    """
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        help_text="ID of the existing user to link this teacher profile to"
    )
    user = UserMinimalSerializer(read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Teacher
        fields = [
            # User Link
            "user_id",
            "user",
            
            # Identity
            "id",
            "teacher_id",
            
            # Personal Info
            "gender",
            "date_of_birth",
            "marital_status",
            "languages_known",
            "class_assigned",
            "subject",
            "blood_group",
            "primary_contact_number",
            "father_name",
            "mother_name",
            "qualification",
            "work_experience",
            
            # Previous Employment
            "previous_school_name",
            "previous_school_address",
            "previous_school_phone",
            
            # Address
            "permanent_address",
            "current_address",
            
            # Identification
            "pan_number",
            
            # Payroll
            "epf_no",
            "basic_salary",
            "contract_type",
            "work_shift",
            "work_location",
            "date_of_joining",
            "date_of_leaving",
            
            # Leaves
            "medical_leaves",
            "casual_leaves",
            "maternity_leaves",
            "sick_leaves",
            
            # Bank Details
            "account_name",
            "account_number",
            "bank_name",
            "branch_name",
            "ifsc_code",
            
            # Transport
            "route_id",
            "vehicle_number",
            "pickup_point",
            
            # Hostel
            "hostel_id",
            "room_no",
            
            # Social Media
            "facebook",
            "instagram",
            "linkedin",
            "youtube",
            "twitter",
            
            # Documents
            "photo",
            "resume",
            "joining_letter",
            
            # Additional
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_user_id(self, user):
        """Ensure the user doesn't already have a teacher profile."""
        if hasattr(user, 'teacher_profile'):
            raise serializers.ValidationError(
                "This user already has a teacher profile."
            )
        return user

    def validate_teacher_id(self, value):
        """Ensure teacher_id is unique."""
        if Teacher.objects.filter(teacher_id=value).exists():
            raise serializers.ValidationError(
                "A teacher with this ID already exists."
            )
        return value


class TeacherUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating teacher profile.
    Used for PUT/PATCH /teachers/{id}/ endpoint.
    """
    user = UserMinimalSerializer(read_only=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Teacher
        fields = [
            # User (read-only, cannot change linked user)
            "user",
            
            # Identity
            "id",
            "teacher_id",
            
            # Personal Info
            "gender",
            "date_of_birth",
            "marital_status",
            "languages_known",
            "class_assigned",
            "subject",
            "blood_group",
            "primary_contact_number",
            "father_name",
            "mother_name",
            "qualification",
            "work_experience",
            
            # Previous Employment
            "previous_school_name",
            "previous_school_address",
            "previous_school_phone",
            
            # Address
            "permanent_address",
            "current_address",
            
            # Identification
            "pan_number",
            
            # Payroll
            "epf_no",
            "basic_salary",
            "contract_type",
            "work_shift",
            "work_location",
            "date_of_joining",
            "date_of_leaving",
            
            # Leaves
            "medical_leaves",
            "casual_leaves",
            "maternity_leaves",
            "sick_leaves",
            
            # Bank Details
            "account_name",
            "account_number",
            "bank_name",
            "branch_name",
            "ifsc_code",
            
            # Transport
            "route_id",
            "vehicle_number",
            "pickup_point",
            
            # Hostel
            "hostel_id",
            "room_no",
            
            # Social Media
            "facebook",
            "instagram",
            "linkedin",
            "youtube",
            "twitter",
            
            # Documents
            "photo",
            "resume",
            "joining_letter",
            
            # Additional
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_teacher_id(self, value):
        """Ensure teacher_id is unique (excluding current instance)."""
        instance = self.instance
        if Teacher.objects.filter(teacher_id=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError(
                "A teacher with this ID already exists."
            )
        return value
