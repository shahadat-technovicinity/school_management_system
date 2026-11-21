from decimal import Decimal, InvalidOperation

from django.db import transaction
from rest_framework import serializers

from apps.students.models import Student
from exam_mm_exam_setup.models import ExamSetup
from exam_mm_exmroutine_exmadmit.models import ExamsRoutine
from exam_mm_exmroutine_exmadmit.utils import student_takes_subject, subject_is_optional
from .models import (
    class_has_practical,
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
            'grace_written': {'required': False},
            'grace_mcq': {'required': False},
            'grace_practical': {'required': False},
        }

    def validate(self, attrs):
        for f in ('grace_written', 'grace_mcq', 'grace_practical'):
            v = attrs.get(f)
            if v is not None and v < 0:
                raise serializers.ValidationError({f: "Grace marks ঋণাত্মক হতে পারবে না।"})
        routine = attrs.get('exam_routine') or getattr(self.instance, 'exam_routine', None)
        if routine is not None and not class_has_practical(routine.academic_class):
            if (attrs.get('grace_practical') or 0) > 0:
                raise serializers.ValidationError({'grace_practical': "এই ক্লাসে practical নেই।"})
        return attrs


class StudentExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    student_roll = serializers.SerializerMethodField(read_only=True)
    has_practical = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentExamResult
        fields = '__all__'
        read_only_fields = [
            'total_marks', 'grace_written', 'grace_mcq', 'grace_practical', 'grace_marks', 'grade', 'gpa',
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


def sections_for_exam_class(exam_id, class_id):
    """
    এই exam + class এর exam setup গুলো থেকে সব সেকশন নেয় (অটোমেটিক)।
    [{'id': 3, 'name': 'A'}, ...]
    """
    if not exam_id or not class_id:
        return []
    found = {}
    setups = ExamSetup.objects.filter(
        exam_name_id=exam_id, academic_class_id=class_id
    ).prefetch_related('sections')
    for setup in setups:
        for section in setup.sections.all():
            found[section.id] = section.name
    return [{'id': sid, 'name': name} for sid, name in sorted(found.items(), key=lambda kv: str(kv[1]))]


def full_marks_for(subject_ids, exam_id, class_id):
    """
    সর্বোচ্চ নম্বর: exam routine এর total_marks থেকে।
    একাধিক বিষয় (গ্রুপের পেপার) হলে সবগুলোর যোগফল, যেমন 100 + 100 = 200।
    কোনো একটা পেপারের routine না থাকলে None (তখন উপরের সীমা যাচাই হয় না)।
    """
    if not exam_id or not class_id or not subject_ids:
        return None
    per_subject = {}
    routines = ExamsRoutine.objects.filter(
        exam_name_id=exam_id, academic_class_id=class_id, subject_id__in=subject_ids
    )
    for routine in routines:
        value = Decimal(str(routine.total_marks))
        per_subject[routine.subject_id] = max(per_subject.get(routine.subject_id, Decimal('0')), value)
    if len(per_subject) < len(set(subject_ids)):
        return None
    return sum(per_subject.values(), Decimal('0'))


class GradeScaleRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScaleRow
        fields = ['id', 'min_percent', 'min_marks', 'grade', 'point']
        ref_name = 'GradeScaleRow'


class GradeScaleSerializer(serializers.ModelSerializer):
    rows = GradeScaleRowSerializer(many=True, allow_empty=False)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)
    exam_name_title = serializers.CharField(source='exam_name.name', read_only=True, default=None)
    class_name = serializers.CharField(source='academic_class.name', read_only=True, default=None)
    section_name = serializers.CharField(source='section.name', read_only=True, default=None)
    exam_sections = serializers.SerializerMethodField(read_only=True)
    max_marks = serializers.SerializerMethodField(read_only=True)
    pass_percent = serializers.SerializerMethodField(read_only=True)
    pass_marks = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GradeScale
        fields = [
            'id', 'subject', 'subject_name', 'group', 'group_name',
            'exam_name', 'exam_name_title',
            'academic_class', 'class_name',
            'section', 'section_name', 'exam_sections',
            'input_mode', 'max_marks', 'pass_percent', 'pass_marks',
            'rows', 'created_at',
        ]
        read_only_fields = ['created_at']
        ref_name = 'GradeScale'

    def get_exam_sections(self, obj):
        return sections_for_exam_class(obj.exam_name_id, obj.academic_class_id)

    def _subject_ids(self, obj):
        if obj.group_id:
            return [s.id for s in obj.group.subjects.all()]
        return [obj.subject_id] if obj.subject_id else []

    def get_max_marks(self, obj):
        value = full_marks_for(self._subject_ids(obj), obj.exam_name_id, obj.academic_class_id)
        return str(value) if value is not None else None

    def get_pass_percent(self, obj):
        if obj.input_mode != GradeScale.INPUT_PERCENT:
            return None
        passing = [r.min_percent for r in obj.rows.all() if r.point > 0 and r.min_percent is not None]
        return min(passing) if passing else None

    def get_pass_marks(self, obj):
        if obj.input_mode != GradeScale.INPUT_MARKS:
            return None
        passing = [r.min_marks for r in obj.rows.all() if r.point > 0 and r.min_marks is not None]
        return min(passing) if passing else None

    def validate(self, attrs):
        inst = self.instance

        def current(name):
            return attrs[name] if name in attrs else getattr(inst, name, None)

        subject = current('subject')
        group = current('group')
        academic_class = current('academic_class')
        exam = current('exam_name')
        section = current('section')
        mode = attrs.get('input_mode') or getattr(inst, 'input_mode', None) or GradeScale.INPUT_PERCENT

        if bool(subject) == bool(group):
            raise serializers.ValidationError("subject অথবা group, দুটোর ঠিক একটা বাছতে হবে।")

        # exam -> class -> section: আগে exam, তারপর class, তারপর (দরকারে) section
        if exam and not academic_class:
            raise serializers.ValidationError({'academic_class': "exam বাছলে class-ও বাছতে হবে।"})
        if section and not (exam and academic_class):
            raise serializers.ValidationError({'section': "section বাছতে হলে আগে exam ও class বাছুন।"})
        if exam:
            setups = list(ExamSetup.objects.filter(
                exam_name=exam, academic_class=academic_class
            ).prefetch_related('sections'))
            if not setups:
                raise serializers.ValidationError("এই exam ও class এর কোনো exam setup নেই। আগে exam setup বানান।")
            if section:
                in_setup = any(section.id in {s.id for s in setup.sections.all()} for setup in setups)
                if not in_setup:
                    raise serializers.ValidationError({'section': "এই section এই exam setup এ নেই।"})

        clash = GradeScale.objects.filter(
            subject=subject, group=group, academic_class=academic_class,
            exam_name=exam, section=section,
        )
        if inst:
            clash = clash.exclude(pk=inst.pk)
        if clash.exists():
            raise serializers.ValidationError("এই বিষয়/গ্রুপ, exam, ক্লাস ও সেকশনের জন্য grade তালিকা আগেই আছে।")

        rows = attrs.get('rows')
        if rows is None and inst and 'input_mode' in attrs and attrs['input_mode'] != inst.input_mode:
            raise serializers.ValidationError({'rows': "input_mode বদলালে সব rows আবার পাঠাতে হবে।"})

        if rows is not None:
            field = 'min_marks' if mode == GradeScale.INPUT_MARKS else 'min_percent'
            other = 'min_percent' if mode == GradeScale.INPUT_MARKS else 'min_marks'
            values = []
            for row in rows:
                if row.get(field) is None:
                    raise serializers.ValidationError({'rows': f"প্রতিটি সারিতে '{field}' দিতে হবে।"})
                values.append(row[field])
                row[other] = None  # অন্য mode এর ঘর ফাঁকা রাখা হয়

            if mode == GradeScale.INPUT_MARKS:
                subject_ids = [s.id for s in group.subjects.all()] if group else [subject.id]
                upper = full_marks_for(
                    subject_ids, exam.id if exam else None, academic_class.id if academic_class else None
                )
                upper_text = f"সর্বোচ্চ নম্বর ({upper}) এর মধ্যে" if upper is not None else "অর্থাৎ 0 বা এর বেশি"
            else:
                upper = Decimal('100')
                upper_text = "0 থেকে 100 এর মধ্যে"

            if len(values) != len(set(values)):
                raise serializers.ValidationError({'rows': "একই মান দুবার দেওয়া যাবে না।"})
            if 0 not in values:
                raise serializers.ValidationError({'rows': "সবচেয়ে নিচের ধাপ 0 থেকে শুরু হতে হবে (সাধারণত F, point 0)।"})
            if any(v < 0 for v in values) or (upper is not None and any(v > upper for v in values)):
                raise serializers.ValidationError({'rows': f"মান {upper_text} হতে হবে।"})
            if any(r['point'] < 0 for r in rows):
                raise serializers.ValidationError({'rows': "point ঋণাত্মক হতে পারে না।"})
            ordered = sorted(rows, key=lambda r: r[field])
            for lower, higher in zip(ordered, ordered[1:]):
                if higher['point'] < lower['point']:
                    raise serializers.ValidationError(
                        {'rows': f"{higher[field]} এর point ({higher['point']}) "
                                 f"{lower[field]} এর চেয়ে কম হতে পারে না।"}
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