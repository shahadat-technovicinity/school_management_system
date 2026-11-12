from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from accounts_mm_fee_type.models import FeeHead
from apps.students.models import Student
from .models import CreateFee, FeeStructureItem


def head_info():
    """সব FeeHead এর তথ্য আর কে কার সন্তান, একবারেই।"""
    info, children = {}, {}
    for r in FeeHead.objects.values('id', 'name', 'parent_id', 'is_active'):
        info[r['id']] = r
        children.setdefault(r['parent_id'], []).append(r['id'])
    return info, children


def get_leaf_ids(fee_head_id, info=None, children=None):
    """বাছা Fee Type এর নিচের একদম শেষ স্তরের (active) fee গুলোর id। নিচে কিছু না থাকলে নিজেই।"""
    if info is None:
        info, children = head_info()
    if not children.get(fee_head_id):
        return [fee_head_id]
    leaves, stack = [], list(children[fee_head_id])
    while stack:
        node = stack.pop()
        kids = children.get(node)
        if kids:
            stack.extend(kids)
        elif info[node]['is_active']:
            leaves.append(node)
    return sorted(leaves)


def head_path(head_id, info):
    names = []
    while head_id is not None:
        names.append(info[head_id]['name'])
        head_id = info[head_id]['parent_id']
    return ' > '.join(reversed(names))


class FeeStructureItemSerializer(serializers.ModelSerializer):
    fee_head_name = serializers.CharField(source='fee_head.name', read_only=True)

    class Meta:
        model = FeeStructureItem
        fields = ['id', 'fee_head', 'fee_head_name', 'amount']
        read_only_fields = ['id']
        ref_name = 'FeeStructureItem'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("টাকা ০ এর বেশি হতে হবে।")
        return value


class FeeStructureSerializer(serializers.ModelSerializer):
    fee_head_name = serializers.CharField(source='fee_head.name', read_only=True)
    class_name = serializers.CharField(source='academic_class.name', read_only=True, default=None)
    section_names = serializers.SerializerMethodField()
    student_details = serializers.SerializerMethodField()
    applies_to_display = serializers.CharField(source='get_applies_to_display', read_only=True)
    payment_period_display = serializers.CharField(source='get_payment_period_display', read_only=True)
    items = FeeStructureItemSerializer(many=True, allow_empty=False)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = CreateFee
        fields = [
            'id', 'fee_head', 'fee_head_name',
            'applies_to', 'applies_to_display',
            'academic_class', 'class_name', 'sections', 'section_names',
            'students', 'student_details',
            'payment_period', 'payment_period_display',
            'valid_from', 'valid_until',
            'items', 'total_amount', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        ref_name = 'CreateFee'

    # ---------- read ----------
    def get_total_amount(self, obj):
        return sum((i.amount for i in obj.items.all()), Decimal('0'))

    def get_section_names(self, obj):
        return [s.name for s in obj.sections.all()]

    def get_student_details(self, obj):
        return [
            {
                'id': s.id,
                'name': getattr(s, 'full_name', str(s)),
                'roll_number': s.roll_number,
            }
            for s in obj.students.all()
        ]

    # ---------- validation ----------
    def validate(self, attrs):
        inst = self.instance

        def val(key):
            if key in attrs:
                return attrs[key]
            if inst is None:
                return None
            if key in ('sections', 'students'):
                return list(getattr(inst, key).all())
            return getattr(inst, key)

        fee_head = val('fee_head')
        applies_to = val('applies_to') or 'class'
        period = val('payment_period')
        valid_from, valid_until = val('valid_from'), val('valid_until')
        academic_class = val('academic_class')
        sections = val('sections') or []
        students = val('students') or []

        if not fee_head.is_active:
            raise serializers.ValidationError({'fee_head': "এই Fee Type টি বন্ধ আছে।"})

        # --- তারিখ ---
        if valid_until < valid_from:
            raise serializers.ValidationError({'valid_until': "শেষ তারিখ শুরুর তারিখের আগে হতে পারে না।"})
        today = timezone.localdate()
        changed_until = inst is None or 'valid_until' in attrs and attrs['valid_until'] != inst.valid_until
        if changed_until and valid_until < today:
            raise serializers.ValidationError({'valid_until': "শেষ তারিখ আজকের আগের হতে পারে না।"})

        # --- কার জন্য ---
        if applies_to == 'class':
            if not academic_class:
                raise serializers.ValidationError({'academic_class': "Class wise fee এ class বাছতে হবে।"})
            if not sections:
                raise serializers.ValidationError({'sections': "কমপক্ষে একটা section বাছতে হবে।"})
            attrs['students'] = []
            students = []
        else:
            if not students:
                raise serializers.ValidationError({'students': "Individual fee এ কমপক্ষে একজন ছাত্র বাছতে হবে।"})
            attrs['academic_class'] = None
            attrs['sections'] = []
            academic_class, sections = None, []

        # --- টাকা বসানোর item গুলো ঠিক আছে কিনা ---
        if 'items' in attrs:
            items = [{'fee_head': i['fee_head'], 'amount': i['amount']} for i in attrs['items']]
        else:
            items = [{'fee_head': i.fee_head, 'amount': i.amount} for i in inst.items.all()]

        info, children = head_info()
        leaf_ids = get_leaf_ids(fee_head.id, info, children)
        given = [i['fee_head'].id for i in items]
        if len(given) != len(set(given)):
            raise serializers.ValidationError({'items': "একই fee দুবার দেওয়া হয়েছে।"})
        missing = [info[i]['name'] for i in leaf_ids if i not in given]
        extra = [info[i]['name'] for i in given if i not in leaf_ids]
        if missing:
            raise serializers.ValidationError({'items': f"এই fee গুলোর টাকা দেওয়া হয়নি: {', '.join(missing)}"})
        if extra:
            raise serializers.ValidationError({'items': f"এই fee গুলো বাছা Fee Type এর অংশ না: {', '.join(extra)}"})

        # --- একই fee একই সময়ে দুবার না ---
        self._check_overlap(leaf_ids, applies_to, academic_class, sections, students, valid_from, valid_until)
        return attrs

    def _check_overlap(self, leaf_ids, applies_to, academic_class, sections, students, start, end):
        base = CreateFee.objects.filter(
            is_active=True,
            items__fee_head_id__in=leaf_ids,
            valid_from__lte=end,
            valid_until__gte=start,
        ).distinct()
        if self.instance:
            base = base.exclude(pk=self.instance.pk)

        section_ids = {s.id for s in sections}

        if applies_to == 'class':
            for ex in base.filter(applies_to='class', academic_class=academic_class).prefetch_related('sections'):
                ex_sections = {s.id for s in ex.sections.all()}
                if ex_sections & section_ids:
                    raise serializers.ValidationError(
                        "এই সময়ে এই class/section এর জন্য এই fee আগে থেকেই আছে। আগেরটা বদলাও বা তারিখ আলাদা দাও।"
                    )
            clash = base.filter(
                applies_to='student',
                students__class_name_static=academic_class,
                students__section_static_id__in=section_ids,
            )
            if clash.exists():
                raise serializers.ValidationError(
                    "এই class এর কিছু ছাত্রের জন্য এই সময়ে এই fee আলাদাভাবে দেওয়া আছে।"
                )
        else:
            student_ids = [s.id for s in students]
            dup = base.filter(applies_to='student', students__id__in=student_ids)
            if dup.exists():
                raise serializers.ValidationError(
                    "কিছু ছাত্রের জন্য এই সময়ে এই fee আগে থেকেই আলাদাভাবে দেওয়া আছে।"
                )
            for st in Student.objects.filter(id__in=student_ids):
                for ex in base.filter(applies_to='class', academic_class_id=st.class_name_static_id) \
                        .prefetch_related('sections'):
                    ex_sections = {s.id for s in ex.sections.all()}
                    if st.section_static_id in ex_sections:
                        name = getattr(st, 'full_name', str(st))
                        raise serializers.ValidationError(
                            f"'{name}' এর class এর জন্য এই সময়ে এই fee আগে থেকেই আছে।"
                        )

    # ---------- write ----------
    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')
        sections = validated_data.pop('sections', [])
        students = validated_data.pop('students', [])
        obj = CreateFee.objects.create(**validated_data)
        obj.sections.set(sections)
        obj.students.set(students)
        FeeStructureItem.objects.bulk_create(
            [FeeStructureItem(structure=obj, fee_head=i['fee_head'], amount=i['amount']) for i in items]
        )
        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)
        sections = validated_data.pop('sections', None)
        students = validated_data.pop('students', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if sections is not None:
            instance.sections.set(sections)
        if students is not None:
            instance.students.set(students)
        if items is not None:
            instance.items.all().delete()
            FeeStructureItem.objects.bulk_create(
                [FeeStructureItem(structure=instance, fee_head=i['fee_head'], amount=i['amount']) for i in items]
            )
        return instance