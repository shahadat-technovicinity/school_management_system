from rest_framework import serializers
from .models import *

class BookDistributionModelSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student_id.full_name')
    book_name = serializers.ReadOnlyField(source='book_id.book_name')

    class Meta:
        model = BookDistributionModel
        fields = [
            'id', 
            'student_id',   
            'student_name', 
            'book_id',      
            'book_name',    
            'issue_date', 
            'return_date', 
            'created_at'
        ]




### Letter Distribution Serializer
class LetterDistributionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student_id.full_name')

    class Meta:
        model = LetterDistribution
        fields = '__all__' 