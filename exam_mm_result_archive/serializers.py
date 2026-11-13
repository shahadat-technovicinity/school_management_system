from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework import serializers

from apps.students.models import Student
from exam_mm_exmroutine_exmadmit.utils import student_takes_subject, subject_is_optional
from .models import (
    ExamResultConfig,
    GradeScale,
    GradeScaleRow,
    StudentExamResult,
    SubjectGroup,
)


def check_student_matches_routine(student, routine):
    """Student এর class ও section routine এর setup এর সাথে মিলছে কিনা দেখে।
    মিললে None, না মিললে error message return করে।"""
    if student.class_name_static_id != routine.academic_class_id:
        return "Student এর class এই routine এর class এর সাথে মিলছে না।"

    setup = routine.exam_setup
    if setup is not None:
        section_id = student.section_static_id
        if not section_id or not setup.sections.filter(id=section_id).exists():
            return "Student এর section এই exam setup এ নেই।"
    return None


def to_decimal(value, label):
    """নম্বর Decimal এ বদলায়। ভুল হলে (None, error) দেয়।"""
    if value in (None, ''):
        return Decimal('0'), None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, f"{label} এর নম্বর সংখ্যা হতে হবে।"
    return number, None


def validate_marks_entry(student, config, written, mcq, practical):
    """
    নম্বর entry র সব যাচাই এক জায়গায়। ঠিক থাকলে None, নাহলে error message।
    - ছাত্রের class/section মেলে কিনা
    - ধর্ম বিষয় হলে ছাত্রের ধর্ম মেলে কিনা
    - নম্বর ঋণাত্মক বা পূর্ণমানের বেশি কিনা
    - একজন ছাত্রের একাধিক ঐচ্ছিক (৪র্থ) বিষয়ের নম্বর দেওয়া হচ্ছে কিনা
    """
    routine = config.exam_routine

    error = check_student_matches_routine(student, routine)
    if error:
        return error

    if not student_takes_subject(student, routine.subject):
        return f"এই ছাত্রের ধর্মে '{routine.subject.name}' বিষয় নেই।"

    parts = [('Written', written, config.written_full_marks), ('MCQ', mcq, config.mcq_full_marks)]
    if config.has_practical:
        parts.append(('Practical', practical, config.practical_full_marks))
    for label, value, full in parts:
        if value < 0:
            return f"{label} এর নম্বর ঋণাত্মক হতে পারে না।"
        if full and Decimal(full) > 0 and value > Decimal(full):
            return f"{label} এর নম্বর ({value}) পূর্ণমান ({full}) এর বেশি।"

    total = sum(v for _, v, _ in parts)
    if total > Decimal(str(config.total_full_marks_calc)):
        return f"মোট নম্বর ({total}) পূর্ণমান ({config.total_full_marks_calc}) এর বেশি।"

    if subject_is_optional(routine.subject) and routine.exam_setup_id:
        others = StudentExamResult.objects.filter(
            student=student, result_config__exam_routine__exam_setup_id=routine.exam_setup_id
        ).exclude(result_config=config).select_related('result_config__exam_routine__subject')
        for other in others:
            other_subject = other.result_config.exam_routine.subject
            if subject_is_optional(other_subject):
                return (
                    f"এই ছাত্রের '{other_subject.name}' এর নম্বর আগেই আছে। "
                    f"একজন ছাত্র একটাই ঐচ্ছিক (৪র্থ) বিষয় নিতে পারে।"
                )
    return None


class ExamResultConfigSerializer(serializers.ModelSerializer):
    has_practical = serializers.BooleanField(read_only=True)
    subject_name = serializers.CharField(source='exam_routine.subject.name', read_only=True)
    class_name = serializers.CharField(source='exam_routine.academic_class.name', read_only=True)
    total_full_marks = serializers.DecimalField(
        source='exam_routine.total_marks',
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = ExamResultConfig
        fields = '__all__'
        extra_kwargs = {
            'written_full_marks': {'required': False},
            'written_pass_marks': {'required': False},
            'mcq_full_marks': {'required': False},
            'mcq_pass_marks': {'required': False},
            'practical_full_marks': {'required': False},
            'practical_pass_marks': {'required': False},
            'grace_marks': {'required': False},
        }

    def validate_grace_marks(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Grace marks ঋণাত্মক হতে পারবে না।")
        return value


class StudentExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    student_roll = serializers.SerializerMethodField(read_only=True)
    has_practical = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentExamResult
        fields = '__all__'
        read_only_fields = [
            'total_marks', 'grace_marks', 'grade', 'gpa',
            'written_status', 'mcq_status',
            'practical_status', 'overall_status',
        ]
        extra_kwargs = {
            'practical_marks': {'required': False},
            'section': {'required': False},
        }

    def get_student_name(self, obj):
        return obj.student.full_name

    def get_student_roll(self, obj):
        return obj.student.roll_number

    def get_has_practical(self, obj):
        return obj.result_config.has_practical

    def validate(self, data):
        result_config = data.get('result_config') or getattr(self.instance, 'result_config', None)
        student = data.get('student') or getattr(self.instance, 'student', None)

        if result_config and not result_config.has_practical:
            data['practical_marks'] = 0

        if result_config and student:
            def pick(name):
                if name in data:
                    return Decimal(str(data[name]))
                if self.instance is not None:
                    return Decimal(str(getattr(self.instance, name)))
                return Decimal('0')

            error = validate_marks_entry(
                student, result_config,
                pick('written_marks'), pick('mcq_marks'), pick('practical_marks'),
            )
            if error:
                raise serializers.ValidationError(error)

        return data


class StudentListForResultSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'roll_number', 'admission_number']


class BulkResultInputSerializer(serializers.Serializer):
    result_config = serializers.IntegerField()
    results = serializers.ListField(child=serializers.DictField())

    def validate_results(self, value):
        for item in value:
            if 'student' not in item:
                raise serializers.ValidationError("প্রতিটি item এ student id লাগবে")
            if 'written_marks' not in item:
                raise serializers.ValidationError("written_marks লাগবে")
            if 'mcq_marks' not in item:
                raise serializers.ValidationError("mcq_marks লাগবে")
        return value


# ---------------------------------------------------------------------------
# Admin: বিষয় গ্রুপ (English = 1st + 2nd paper) ও Grade তালিকা
# ---------------------------------------------------------------------------
class SubjectGroupSerializer(serializers.ModelSerializer):
    subject_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubjectGroup
        fields = ['id', 'name', 'subjects', 'subject_names', 'created_at']
        read_only_fields = ['created_at']
        ref_name = 'SubjectGroup'

    def get_subject_names(self, obj):
        return [s.name for s in obj.subjects.all()]

    def validate_subjects(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("কমপক্ষে দুটো বিষয় (পেপার) বাছতে হবে।")
        clash = SubjectGroup.objects.filter(subjects__in=value)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError(
                f"কিছু বিষয় আগে থেকেই '{clash.first().name}' গ্রুপে আছে।"
            )
        return value


class GradeScaleRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScaleRow
        fields = ['id', 'min_percent', 'grade', 'point']
        ref_name = 'GradeScaleRow'


class GradeScaleSerializer(serializers.ModelSerializer):
    rows = GradeScaleRowSerializer(many=True, allow_empty=False)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)
    class_name = serializers.CharField(source='academic_class.name', read_only=True, default=None)
    pass_percent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GradeScale
        fields = [
            'id', 'subject', 'subject_name', 'group', 'group_name',
            'academic_class', 'class_name', 'pass_percent', 'rows', 'created_at',
        ]
        read_only_fields = ['created_at']
        ref_name = 'GradeScale'

    def get_pass_percent(self, obj):
        passing = [r.min_percent for r in obj.rows.all() if r.point > 0]
        return min(passing) if passing else None

    def validate(self, attrs):
        inst = self.instance
        subject = attrs['subject'] if 'subject' in attrs else getattr(inst, 'subject', None)
        group = attrs['group'] if 'group' in attrs else getattr(inst, 'group', None)
        academic_class = attrs['academic_class'] if 'academic_class' in attrs else getattr(inst, 'academic_class', None)

        if bool(subject) == bool(group):
            raise serializers.ValidationError("subject অথবা group, দুটোর ঠিক একটা বাছতে হবে।")

        clash = GradeScale.objects.filter(
            subject=subject, group=group, academic_class=academic_class
        )
        if inst:
            clash = clash.exclude(pk=inst.pk)
        if clash.exists():
            raise serializers.ValidationError("এই বিষয়/গ্রুপ ও ক্লাসের জন্য grade তালিকা আগেই আছে।")

        rows = attrs.get('rows')
        if rows is not None:
            percents = [r['min_percent'] for r in rows]
            if len(percents) != len(set(percents)):
                raise serializers.ValidationError({'rows': "একই শতকরা দুবার দেওয়া যাবে না।"})
            if 0 not in percents:
                raise serializers.ValidationError({'rows': "সবচেয়ে নিচের ধাপ 0% থেকে শুরু হতে হবে (সাধারণত F, point 0)।"})
            if any(p < 0 or p > 100 for p in percents):
                raise serializers.ValidationError({'rows': "শতকরা 0 থেকে 100 এর মধ্যে হতে হবে।"})
            if any(r['point'] < 0 for r in rows):
                raise serializers.ValidationError({'rows': "point ঋণাত্মক হতে পারে না।"})
            ordered = sorted(rows, key=lambda r: r['min_percent'])
            for lower, higher in zip(ordered, ordered[1:]):
                if higher['point'] < lower['point']:
                    raise serializers.ValidationError(
                        {'rows': f"{higher['min_percent']}% এর point ({higher['point']}) "
                                 f"{lower['min_percent']}% এর চেয়ে কম হতে পারে না।"}
                    )
            if not any(r['point'] == 0 for r in rows):
                raise serializers.ValidationError({'rows': "fail এর জন্য point 0 এর একটা ধাপ লাগবে।"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        rows = validated_data.pop('rows')
        scale = GradeScale.objects.create(**validated_data)
        GradeScaleRow.objects.bulk_create([GradeScaleRow(scale=scale, **r) for r in rows])
        return scale

    @transaction.atomic
    def update(self, instance, validated_data):
        rows = validated_data.pop('rows', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if rows is not None:
            instance.rows.all().delete()
            GradeScaleRow.objects.bulk_create([GradeScaleRow(scale=instance, **r) for r in rows])
        return instance