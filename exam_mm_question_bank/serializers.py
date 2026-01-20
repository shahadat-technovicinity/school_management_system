# qna_app/serializers.py
from rest_framework import serializers
from .models import *

class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExmQuestionBank
        fields = '__all__'
        read_only_fields = ['id', 'date_created', 'uploaded_by'] 

    def validate_pdf_file(self, value):
        if not value:
            return value
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("ফাইলটি PDF (.pdf) হতে হবে।")
        if value.size > 10*1024*1024:
            raise serializers.ValidationError("ফাইল 10MB এর বেশি হতে পারবে না।")
        return value