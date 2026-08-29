from rest_framework import serializers
from django.contrib.auth import get_user_model
from academic_create_subject.models import Subject_Name
from .models import Teacher

User = get_user_model()


class TeachersListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)
    value = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["value", "label"]
        ref_name = "TeacherMMUserListDropdown"


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "username", "role", "phone_number", "is_active"]
        read_only_fields = ["id", "is_active"]
        ref_name = "TeacherMMUserMinimal"


class TeacherListSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id", "user", "full_name", "name_bn", "gender", "subject", "subject_name",
            "class_assigned", "class_name", "primary_contact_number", "status",
            "date_of_joining", "photo", "resume", "joining_letter", "office_order_copy",
            "nid_card_copy", "created_at", "updated_at"
        ]
        ref_name = "TeacherMMTeacherList"


class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id", "user", "full_name", "name_bn", "email",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "class_name", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "father_name_bn", "mother_name", "mother_name_bn",
            "qualification", "work_experience",
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
        ref_name = "TeacherMMTeacherDetail"


class TeacherCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        help_text="ID of the existing user (role='Teacher') to link this teacher profile to"
    )
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
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
        model = Teacher
        fields = [
            "user_id", "id", "name_bn",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "father_name_bn", "mother_name", "mother_name_bn",
            "qualification", "work_experience",
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
        ref_name = "TeacherMMTeacherCreate"

    def validate_user_id(self, user):
        if hasattr(user, 'role') and user.role and user.role.name.lower() != 'teacher':
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
        model = Teacher
        fields = [
            "user", "id", "name_bn",
            "gender", "date_of_birth", "marital_status", "languages_known",
            "class_assigned", "subject", "subject_name", "blood_group",
            "primary_contact_number", "father_name", "father_name_bn", "mother_name", "mother_name_bn",
            "qualification", "work_experience",
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
        ref_name = "TeacherMMTeacherUpdate"