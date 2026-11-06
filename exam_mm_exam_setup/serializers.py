from rest_framework import serializers
from .models import ExamName, ExamSetup


class ExamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamName
        fields = ['id', 'name', 'description', 'is_active', 'created_at']


class ExamSetupSerializer(serializers.ModelSerializer):
    exam_name_title = serializers.ReadOnlyField(source='exam_name.name')
    class_name_text = serializers.ReadOnlyField(source='academic_class.name')
    section_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name', source='sections'
    )

    class Meta:
        model = ExamSetup
        fields = [
            'id',
            'exam_name',
            'exam_name_title',
            'academic_class',
            'class_name_text',
            'sections',
            'section_names',
            'shift',
            'created_at',
        ]

    def validate(self, attrs):
        exam_name = attrs.get('exam_name') or getattr(self.instance, 'exam_name', None)
        academic_class = attrs.get('academic_class') or getattr(self.instance, 'academic_class', None)

        sections = attrs.get('sections')
        if sections is None and self.instance:
            sections = list(self.instance.sections.all())

        others = ExamSetup.objects.filter(
            exam_name=exam_name,
            academic_class=academic_class
        )
        if self.instance:
            others = others.exclude(pk=self.instance.pk)

        for section in sections or []:
            if others.filter(sections=section).exists():
                raise serializers.ValidationError(
                    f"Section '{section.name}' এই exam এ আগে থেকেই setup করা আছে।"
                )
        return attrs