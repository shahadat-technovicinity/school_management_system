from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TeacherAndStaffProfile

User = get_user_model()


class EmployeeUserDropdownSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)
    value = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["value", "label"]
        ref_name = "TeacherStaffUserListDropdowns"


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "username", "role", "phone_number", "is_active"]
        read_only_fields = ["id", "is_active"]
        ref_name = "TeacherStaffUserMinimals"


class TeacherAndStaffListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = TeacherAndStaffProfile
        fields = [
            "id", "user", "employee_type", "designation", "department",
            "full_name", "name_bn", "gender", "primary_contact_number",
            "status", "date_of_joining", "photo", "resume", "joining_letter",
            "office_order_copy", "nid_card_copy", "created_at", "updated_at"
        ]
        ref_name = "TeacherStaffLists"


class TeacherAndStaffDetailSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = TeacherAndStaffProfile
        fields = [
            "id", "user", "employee_type", "designation", "department",
            "full_name", "name_bn", "email", "gender", "date_of_birth",
            "marital_status", "languages_known", "blood_group",
            "primary_contact_number", "father_name", "father_name_bn",
            "mother_name", "mother_name_bn", "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "district", "permanent_address", "current_address", "nid_number", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter", "office_order_copy", "nid_card_copy",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        ref_name = "TeacherStaffDetails"


class TeacherAndStaffCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        help_text="ID of the existing user to link this profile to"
    )

    # File Fields
    photo = serializers.ImageField(required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    office_order_copy = serializers.FileField(required=False, allow_null=True)
    nid_card_copy = serializers.FileField(required=False, allow_null=True)

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
        model = TeacherAndStaffProfile
        fields = [
            "user_id", "id", "employee_type", "designation", "department", "name_bn",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "blood_group", "primary_contact_number", "father_name", "father_name_bn",
            "mother_name", "mother_name_bn", "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "district", "permanent_address", "current_address", "nid_number", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter", "office_order_copy", "nid_card_copy",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        ref_name = "TeacherStaffCreates"

    def validate_user_id(self, user):
        # 1. Role validation (Teacher or Staff check)
        user_role = getattr(user.role, 'name', '') if user.role else ''
        if user_role.lower() not in ['teacher', 'staff']:
            raise serializers.ValidationError(
                "Selected user must have role 'Teacher' or 'Staff'."
            )

        # 2. Existing profile check
        try:
            _ = user.teacher_staff_profile
            raise serializers.ValidationError(
                "This user already has a teacher or staff profile."
            )
        except TeacherAndStaffProfile.DoesNotExist:
            pass

        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserMinimalSerializer(instance.user).data if instance.user else None
        return rep


class TeacherAndStaffUpdateSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    # File Fields
    photo = serializers.ImageField(required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)
    joining_letter = serializers.FileField(required=False, allow_null=True)
    office_order_copy = serializers.FileField(required=False, allow_null=True)
    nid_card_copy = serializers.FileField(required=False, allow_null=True)

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
        model = TeacherAndStaffProfile
        fields = [
            "user", "id", "employee_type", "designation", "department", "name_bn",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "blood_group", "primary_contact_number", "father_name", "father_name_bn",
            "mother_name", "mother_name_bn", "qualification", "work_experience",
            "previous_school_name", "previous_school_address", "previous_school_phone",
            "district", "permanent_address", "current_address", "nid_number", "pan_number",
            "epf_no", "basic_salary", "contract_type", "work_shift",
            "work_location", "date_of_joining", "date_of_leaving",
            "medical_leaves", "casual_leaves", "maternity_leaves", "sick_leaves",
            "account_name", "account_number", "bank_name", "branch_name", "ifsc_code",
            "route_id", "vehicle_number", "pickup_point",
            "hostel_id", "room_no",
            "facebook", "instagram", "linkedin", "youtube", "twitter",
            "photo", "resume", "joining_letter", "office_order_copy", "nid_card_copy",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
        ref_name = "TeacherStaffUpdates"