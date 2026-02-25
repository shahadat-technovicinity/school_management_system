from rest_framework import serializers
from student_profile.models import StudentPersonalInfo
from .models import GeneratedIDCard, IDCardTemplate

class IDCardStatusSerializer(serializers.Serializer):
    """
    Helper to tell the frontend if a card exists
    """
    is_generated = serializers.BooleanField()
    card_image_url = serializers.ImageField(read_only=True)
    generated_date = serializers.DateTimeField(read_only=True)

class StudentIDCardSerializer(serializers.ModelSerializer):
    # Computed fields to make frontend easier
    full_name = serializers.SerializerMethodField()
    class_label = serializers.CharField(source='class_name', read_only=True) # "Class 6"
    section_label = serializers.CharField(source='section', read_only=True)  # "Section A"
    
    # Check if card exists
    id_card_status = serializers.SerializerMethodField()

    class Meta:
        model = StudentPersonalInfo
        fields = [
            'id', 'admission_number', 'roll_number', 'full_name', 
            'class_label', 'section_label', 'blood_group', 'photo', 
            'id_card_status'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name or ''}".strip()

    def get_id_card_status(self, obj):
        # Check if a card exists for this student
        card = GeneratedIDCard.objects.filter(student=obj).order_by('-created_at').first()
        if card:
            return {
                'is_generated': True,
                'card_image_url': card.card_image.url if card.card_image else None,
                'generated_date': card.created_at
            }
        return {'is_generated': False, 'card_image_url': None, 'generated_date': None}

class GenerateCardRequestSerializer(serializers.Serializer):
    student_ids = serializers.ListField(child=serializers.IntegerField())
    template_id = serializers.IntegerField(required=False, default=1)