from decimal import Decimal

from django.db import models
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from academic_create_subject.models import Subject_Name
from exam_mm_exmroutine_exmadmit.models import ExamsRoutine
from exam_mm_exam_setup.models import ExamSetup


# ---------------------------------------------------------------------------
# Grade হিসাব
# ---------------------------------------------------------------------------
def calculate_grade_and_gpa(percentage):
    """Admin কোনো grade তালিকা না দিলে এই সাধারণ তালিকা চলে।"""
    if percentage >= 80:
        return 'A+', 5.0
    elif percentage >= 70:
        return 'A', 4.0
    elif percentage >= 60:
        return 'A-', 3.5
    elif percentage >= 50:
        return 'B', 3.0
    elif percentage >= 40:
        return 'C', 2.0
    elif percentage >= 33:
        return 'D', 1.0
    else:
        return 'F', 0.0


def class_has_practical(academic_class):
    """ক্লাস ৯ ও ১০ এ practical থাকে (class এর numeric_value দেখে, id দেখে নয়)।"""
    value = getattr(academic_class, 'numeric_value', None)
    return value is not None and value >= 9


class SubjectGroup(models.Model):
    """
    দুই (বা বেশি) পেপার মিলিয়ে একটা বিষয়ের result, যেমন English = 1st Paper + 2nd Paper।
    Admin নিজে বেছে দেয়, নাম মিলিয়ে নয়।
    """
    name = models.CharField(max_length=150, unique=True, help_text="যেমন: English, Bangla")
    subjects = models.ManyToManyField(Subject_Name, related_name='result_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GradeScale(models.Model):
    """
    কোন বিষয়ে (বা বিষয় গ্রুপে) শতকরা কত পেলে কোন grade/point, তা admin ঠিক করে।
    পূর্ণমান আর pass mark আসে exam routine ও result-config থেকে (এখানে কোনো পূর্ণমান ধরা হয় না)।
    academic_class ফাঁকা হলে সব ক্লাসের জন্য।
    """
    subject = models.ForeignKey(
        Subject_Name, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    group = models.ForeignKey(
        SubjectGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    academic_class = models.ForeignKey(
        AcademicClass, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.group.name if self.group_id else (self.subject.name if self.subject_id else '-')
        return f"{target} / {self.academic_class or 'all classes'}"


class GradeScaleRow(models.Model):
    scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE, related_name='rows')
    min_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="শতকরা এত বা এর বেশি পেলে")
    grade = models.CharField(max_length=5)
    point = models.DecimalField(max_digits=3, decimal_places=2, help_text="0 হলে fail")

    class Meta:
        ordering = ['-min_percent']

    def __str__(self):
        return f"{self.min_percent}%+ -> {self.grade} ({self.point})"


def find_scale(subject_id, class_id, group_id=None):
    qs = GradeScale.objects.prefetch_related('rows')
    qs = qs.filter(group_id=group_id) if group_id else qs.filter(subject_id=subject_id)
    return qs.filter(academic_class_id=class_id).first() or qs.filter(academic_class__isnull=True).first()


def grade_from_scale(scale, obtained, full):
    """(grade, point) দেয়। শতকরা হিসাব করে admin এর তালিকা থেকে grade খোঁজে।"""
    percent = (float(obtained) / float(full)) * 100 if full and float(full) > 0 else 0.0
    for row in sorted(scale.rows.all(), key=lambda r: r.min_percent, reverse=True):
        if percent + 1e-9 >= float(row.min_percent):
            return row.grade, float(row.point)
    return 'F', 0.0


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
class ExamResultConfig(models.Model):
    exam_routine = models.OneToOneField(
        ExamsRoutine,
        on_delete=models.CASCADE,
        related_name='result_config',
        help_text="Linked ExamsRoutine"
    )
    written_full_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    written_pass_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mcq_full_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mcq_pass_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_full_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_pass_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Grace marks: এই বিষয়ের সবার মোট নম্বরের সাথে যোগ হবে (পূর্ণমান ছাড়াবে না)। 0 = নেই"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Exam Result Config"

    def __str__(self):
        return f"Config: {self.exam_routine}"

    @property
    def has_practical(self):
        try:
            return class_has_practical(self.exam_routine.academic_class)
        except Exception:
            return False

    @property
    def total_pass_marks_calc(self):
        """written + mcq (+ practical) এর pass mark এর যোগফল (exam routine এর result-config এ admin যা দিয়েছে)।"""
        total = float(self.written_pass_marks) + float(self.mcq_pass_marks)
        if self.has_practical:
            total += float(self.practical_pass_marks)
        return total

    @property
    def total_full_marks_calc(self):
        """written + mcq (+ practical) এর পূর্ণমান; এগুলো 0 থাকলে routine এর পূর্ণমান।"""
        full = float(self.written_full_marks) + float(self.mcq_full_marks)
        if self.has_practical:
            full += float(self.practical_full_marks)
        if full <= 0:
            full = float(self.exam_routine.total_marks)
        return full


class StudentExamResult(models.Model):
    STATUS_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ]

    result_config = models.ForeignKey(
        ExamResultConfig,
        on_delete=models.CASCADE,
        related_name='student_results',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_results',
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='exam_results',
    )

    written_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mcq_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    grace_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # আসলে যতটুকু যোগ হয়েছে (হিসাব করা)

    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grade = models.CharField(max_length=5, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    written_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='fail')
    mcq_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='fail')
    practical_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pass')
    overall_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='fail')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('result_config', 'student')
        verbose_name = "Student Exam Result"

    def __str__(self):
        return f"{self.student} - {self.grade}"

    def calculate_result(self):
        config = self.result_config
        routine = config.exam_routine
        has_practical = config.has_practical

        # ক্লাস ৬-৮ এ practical নেই
        if not has_practical:
            self.practical_marks = 0

        full = config.total_full_marks_calc

        # Grace marks: admin এর দেওয়া সংখ্যা সবার মোট নম্বরে যোগ হয়, তবে পূর্ণমান ছাড়ায় না
        raw_total = self.written_marks + self.mcq_marks + self.practical_marks
        room = max(Decimal(str(full)) - raw_total, Decimal('0'))
        self.grace_marks = min(config.grace_marks or Decimal('0'), room)
        self.total_marks = raw_total + self.grace_marks

        # Grade/GPA: admin এর তালিকা থাকলে সেটা, নাহলে সাধারণ তালিকা
        scale = find_scale(routine.subject_id, routine.academic_class_id)
        if scale:
            self.grade, gpa = grade_from_scale(scale, self.total_marks, full)
        else:
            percentage = (float(self.total_marks) / full) * 100 if full > 0 else 0
            self.grade, gpa = calculate_grade_and_gpa(percentage)

        # admin এর দেওয়া মোট pass mark এর নিচে হলে fail
        pass_total = config.total_pass_marks_calc
        if pass_total > 0 and float(self.total_marks) < pass_total:
            self.grade, gpa = 'F', 0.0
        self.gpa = gpa

        if has_practical:
            # ক্লাস ৯-১০: written, mcq, practical প্রতিটায় আলাদা করে pass করতে হবে
            # grace marks written অংশের সাথে ধরা হয়
            self.written_status = 'pass' if (self.written_marks + self.grace_marks) >= config.written_pass_marks else 'fail'
            self.mcq_status = 'pass' if self.mcq_marks >= config.mcq_pass_marks else 'fail'
            self.practical_status = 'pass' if self.practical_marks >= config.practical_pass_marks else 'fail'
            statuses = [self.written_status, self.mcq_status, self.practical_status]
            self.overall_status = 'pass' if all(s == 'pass' for s in statuses) and gpa > 0 else 'fail'
        else:
            # ক্লাস ৬-৮: written + mcq মিলিয়ে মোট নম্বরেই pass/fail
            self.overall_status = 'pass' if gpa > 0 else 'fail'
            self.written_status = self.overall_status
            self.mcq_status = self.overall_status
            self.practical_status = 'pass'

    def save(self, *args, **kwargs):
        self.calculate_result()
        # update_or_create শুধু দেওয়া field সেভ করে (update_fields), তাই হিসাব করা field গুলোও যোগ করে দিই,
        # নাহলে নম্বর বদলালে total/grade/GPA আগের মতোই থেকে যায়
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {
                'total_marks', 'grace_marks', 'grade', 'gpa',
                'written_status', 'mcq_status', 'practical_status', 'overall_status',
            }
        super().save(*args, **kwargs)


class CombinedResultConfig(models.Model):
    """
    Admin এখানে ঠিক করে কোন কোন exam setup এর result মিলিয়ে বার্ষিক result হবে।
    যেমন: Half Yearly (দশম-A setup) + Final (দশম-A setup)।
    কোনো মার্ক আলাদা করে ঢোকানো হয় না, archive এর StudentExamResult থেকেই যোগ হয়।
    """
    name = models.CharField(max_length=150, help_text="যেমন: Annual Result 2026")
    academic_class = models.ForeignKey(
        AcademicClass,
        on_delete=models.CASCADE,
        related_name='combined_result_configs',
    )
    exam_setups = models.ManyToManyField(
        ExamSetup,
        related_name='combined_result_configs',
        help_text="যে setup গুলোর result যোগ হবে (Half Yearly + Final)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Combined Result Config"

    def __str__(self):
        return f"{self.name} - {self.academic_class}"