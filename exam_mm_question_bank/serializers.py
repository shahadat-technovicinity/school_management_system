from rest_framework import serializers
from .models import ExmQuestionBank


# --- 1. User Serializer (status is read-only) ---
class UserQuestionBankSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = ExmQuestionBank
        fields = '__all__'
        read_only_fields = ['id', 'date_created', 'uploaded_by', 'status'] 
        ref_name = 'UserExmQuestionBankSerializer'

    def validate_pdf_file(self, value):
        if not value:
            return value
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("ফাইলটি PDF (.pdf) হতে হবে।")
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("ফাইল 10MB এর বেশি হতে পারবে না।")
        return value


# --- 2. Admin Serializer ---
class AdminQuestionBankSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = ExmQuestionBank
        fields = '__all__'
        read_only_fields = ['id', 'date_created', 'uploaded_by'] 
        ref_name = 'AdminExmQuestionBankSerializer'


# --- 3. Admin Status Update Serializer (Swagger-এ শুধু status দেখাবে) ---
class QuestionStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExmQuestionBank
        fields = ['status']