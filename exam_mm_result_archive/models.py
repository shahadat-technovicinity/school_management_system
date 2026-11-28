import uuid
from decimal import Decimal

from django.db import models
from django.db.models import Q
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from academic_create_subject.models import Subject_Name
from exam_mm_exmroutine_exmadmit.models import ExamsRoutine
from exam_mm_exam_setup.models import ExamSetup


def _exam_name_model():
    """ExamSetup.exam_name যে model এর FK, সেটাই নেয় (নাম/app আলাদা করে লিখতে হয় না)।"""
    related = ExamSetup._meta.get_field('exam_name').remote_field.model
    if isinstance(related, str):
        return related if '.' in related else f"{ExamSetup._meta.app_label}.{related}"
    return related


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
    কোন বিষয়ে (বা বিষয় গ্রুপে) কত পেলে কোন grade/point, তা admin ঠিক করে।

    কোন পরীক্ষার জন্য: exam_name (ফাঁকা হলে সব পরীক্ষার জন্য)
    কোন ক্লাসের জন্য:  academic_class (ফাঁকা হলে সব ক্লাসের জন্য)
    কোন সেকশনের জন্য: section (ফাঁকা হলে ওই exam setup এর সব সেকশন; ক্লাস ৯-১০ এ আলাদা সেকশন বাছা যায়)

    input_mode:
      percent -> সারিতে শতকরা (0-100) দেওয়া হয়
      marks   -> সারিতে সরাসরি নম্বর দেওয়া হয়; সর্বোচ্চ নম্বর আসে exam routine এর total_marks থেকে
                 (গ্রুপ হলে সব পেপারের যোগফল, যেমন 100 + 100 = 200)
    """
    INPUT_PERCENT = 'percent'
    INPUT_MARKS = 'marks'
    INPUT_CHOICES = [
        (INPUT_PERCENT, 'Percent'),
        (INPUT_MARKS, 'Marks'),
    ]

    subject = models.ForeignKey(
        Subject_Name, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    group = models.ForeignKey(
        SubjectGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    exam_name = models.ForeignKey(
        _exam_name_model(), on_delete=models.CASCADE, null=True, blank=True,
        related_name='result_grade_scales',
    )
    academic_class = models.ForeignKey(
        AcademicClass, on_delete=models.CASCADE, null=True, blank=True, related_name='grade_scales'
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True, related_name='result_grade_scales'
    )
    input_mode = models.CharField(max_length=10, choices=INPUT_CHOICES, default=INPUT_PERCENT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.group.name if self.group_id else (self.subject.name if self.subject_id else '-')
        return f"{target} / {self.exam_name or 'all exams'} / {self.academic_class or 'all classes'}"


class GradeScaleRow(models.Model):
    scale = models.ForeignKey(GradeScale, on_delete=models.CASCADE, related_name='rows')
    min_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="percent mode: শতকরা এত বা এর বেশি পেলে",
    )
    min_marks = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="marks mode: নম্বর এত বা এর বেশি পেলে",
    )
    grade = models.CharField(max_length=5)
    point = models.DecimalField(max_digits=3, decimal_places=2, help_text="0 হলে fail")

    class Meta:
        ordering = ['-min_percent', '-min_marks']

    def __str__(self):
        if self.min_marks is not None:
            return f"{self.min_marks} marks+ -> {self.grade} ({self.point})"
        return f"{self.min_percent}%+ -> {self.grade} ({self.point})"


def pick_scale(candidates, exam_id=None, section_id=None):
    """
    একাধিক grade তালিকার মধ্যে সবচেয়ে নির্দিষ্টটা বাছে।
    exam মিললে সবচেয়ে বেশি গুরুত্ব, তারপর section, তারপর class।
    exam_id=None দিলে (একাধিক পরীক্ষা যোগ করার সময়) শুধু 'সব পরীক্ষার' তালিকা চলে।
    """
    best, best_score = None, -1
    for scale in candidates:
        if scale.exam_name_id and scale.exam_name_id != exam_id:
            continue
        if scale.section_id and scale.section_id != section_id:
            continue
        score = (4 if scale.exam_name_id else 0) + (2 if scale.section_id else 0) + (1 if scale.academic_class_id else 0)
        if score > best_score:
            best, best_score = scale, score
    return best


def find_scale(subject_id, class_id, group_id=None, exam_id=None, section_id=None):
    qs = GradeScale.objects.prefetch_related('rows')
    qs = qs.filter(group_id=group_id) if group_id else qs.filter(subject_id=subject_id)
    qs = qs.filter(Q(academic_class_id=class_id) | Q(academic_class__isnull=True))
    return pick_scale(qs, exam_id, section_id)


def grade_from_scale(scale, obtained, full):
    """(grade, point) দেয়। percent mode এ শতকরা, marks mode এ সরাসরি নম্বর মিলিয়ে grade খোঁজে।"""
    if scale.input_mode == GradeScale.INPUT_MARKS:
        value = float(obtained)

        def threshold(row):
            return float(row.min_marks or 0)
    else:
        value = (float(obtained) / float(full)) * 100 if full and float(full) > 0 else 0.0

        def threshold(row):
            return float(row.min_percent or 0)

    for row in sorted(scale.rows.all(), key=threshold, reverse=True):
        if value + 1e-9 >= threshold(row):
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
    # Grace marks: প্রতিটা অংশে আলাদা। প্রতিজনের ওই অংশের নম্বরের সাথে যোগ হয় (ওই অংশের পূর্ণমান ছাড়ায় না)
    grace_written = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_mcq = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_practical = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # শুধু ক্লাস ৯-১০
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

    # আসলে যতটুকু grace যোগ হয়েছে (হিসাব করা, অংশ অনুযায়ী) এবং তাদের যোগফল
    grace_written = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_mcq = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_practical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)

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

        # Grace marks: written / mcq / practical প্রতিটায় আলাদা।
        # শুধু যে ছাত্র ওই অংশে ফেল (নম্বর < ওই অংশের pass marks) তারই ওই অংশে grace যোগ হয়;
        # যে পাস করেছে তার নম্বর বদলায় না। যোগ হলে ওই অংশের পূর্ণমান ছাড়ায় না।
        def _grace(raw, grace, part_full, part_pass):
            grace = grace or Decimal('0')
            part_pass = Decimal(str(part_pass or 0))
            if grace <= 0 or raw >= part_pass:
                return Decimal('0')
            part_full = Decimal(str(part_full or 0))
            if part_full > 0:
                grace = min(grace, max(part_full - raw, Decimal('0')))
            return max(grace, Decimal('0'))

        gw = _grace(self.written_marks, config.grace_written, config.written_full_marks, config.written_pass_marks)
        gm = _grace(self.mcq_marks, config.grace_mcq, config.mcq_full_marks, config.mcq_pass_marks)
        gp = _grace(self.practical_marks, config.grace_practical, config.practical_full_marks,
                    config.practical_pass_marks) if has_practical else Decimal('0')

        # মোট পূর্ণমান ছাড়াবে না (ছাড়ালে practical, তারপর mcq, তারপর written থেকে কমে)
        raw_total = self.written_marks + self.mcq_marks + self.practical_marks
        room = max(Decimal(str(full)) - raw_total, Decimal('0'))
        excess = gw + gm + gp - room
        if excess > 0:
            cut = min(excess, gp); gp -= cut; excess -= cut
            cut = min(excess, gm); gm -= cut; excess -= cut
            cut = min(excess, gw); gw -= cut; excess -= cut

        self.grace_written, self.grace_mcq, self.grace_practical = gw, gm, gp
        self.grace_marks = gw + gm + gp
        self.total_marks = raw_total + self.grace_marks

        # Grade/GPA: শুধু admin এর Grade Scale থেকে (এই বিষয়/exam/class/section এর জন্য)।
        # Scale না থাকলে নিজে থেকে grade বসানো হয় না: grade ফাঁকা, GPA 0 (pass/fail হয় pass marks দিয়ে)
        section_id = self.section_id or getattr(self.student, 'section_static_id', None)
        scale = find_scale(
            routine.subject_id, routine.academic_class_id,
            exam_id=routine.exam_name_id, section_id=section_id,
        )
        if scale:
            self.grade, gpa = grade_from_scale(scale, self.total_marks, full)
        else:
            self.grade, gpa = '', 0.0

        # admin এর দেওয়া মোট pass mark এর নিচে হলে fail
        pass_total = config.total_pass_marks_calc
        below_total = pass_total > 0 and float(self.total_marks) < pass_total
        if below_total:
            self.grade, gpa = 'F', 0.0
        self.gpa = gpa

        # সব ক্লাসেই: প্রতিটা অংশ (written, mcq, এবং ক্লাস ৯-১০ এ practical) নিজের pass marks পার করতে হবে।
        # কোনো অংশের pass marks 0 দিলে ওই অংশের আলাদা শর্ত থাকে না। প্রতিটা অংশের নিজের grace ওই অংশের সাথে ধরা হয়।
        self.written_status = 'pass' if (self.written_marks + gw) >= config.written_pass_marks else 'fail'
        self.mcq_status = 'pass' if (self.mcq_marks + gm) >= config.mcq_pass_marks else 'fail'
        if has_practical:
            self.practical_status = 'pass' if (self.practical_marks + gp) >= config.practical_pass_marks else 'fail'
        else:
            self.practical_status = 'pass'
        statuses = [self.written_status, self.mcq_status, self.practical_status]
        if any(s == 'fail' for s in statuses):
            # যেকোনো একটা অংশে fail করলে grade F, GPA 0 (কোন অংশে fail তা *_status ফিল্ডে থাকে)
            self.grade, gpa, self.gpa = 'F', 0.0, 0.0
        grade_ok = (gpa > 0) if scale else True  # scale না থাকলে শুধু pass marks দেখা হয়
        self.overall_status = 'pass' if all(s == 'pass' for s in statuses) and not below_total and grade_ok else 'fail'

    def save(self, *args, **kwargs):
        self.calculate_result()
        # update_or_create শুধু দেওয়া field সেভ করে (update_fields), তাই হিসাব করা field গুলোও যোগ করে দিই,
        # নাহলে নম্বর বদলালে total/grade/GPA আগের মতোই থেকে যায়
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {
                'total_marks', 'grace_written', 'grace_mcq', 'grace_practical', 'grace_marks', 'grade', 'gpa',
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




class MarksEntryLog(models.Model):
    """
    প্রতিবার marks save/update হলে এখানে একটা রেকর্ড জমা হয় (কে, কখন, আগে কত ছিল, এখন কত)।
    পরে কেউ নম্বর বদলালে এই log দেখে ধরা যায়, আর রিসিপ্ট PDF হিসেবে নামিয়ে রাখা যায়।
    """
    batch_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    result_config = models.ForeignKey(ExamResultConfig, on_delete=models.CASCADE, related_name='entry_logs')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks_entry_logs')
    action = models.CharField(max_length=10)  # created / updated / unchanged

    old_written = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    old_mcq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    old_practical = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_written = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    new_mcq = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    new_practical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    new_total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    new_grade = models.CharField(max_length=5, blank=True)

    entered_by = models.CharField(max_length=150, blank=True)       # যে নম্বর দিল তার নাম
    entered_by_role = models.CharField(max_length=80, blank=True)   # তার রোল (Admin / Teacher / Staff ...)
    entered_by_id = models.PositiveIntegerField(null=True, blank=True)  # তার user id
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = "Marks Entry Log"

    def __str__(self):
        return f"{self.student_id} {self.action} {self.created_at:%Y-%m-%d %H:%M}"


class ResultPublishSchedule(models.Model):
    """
    Result কখন সবার জন্য প্রকাশ হবে — Admin ক্লাস/সেকশন/exam (বা combined) অনুযায়ী তারিখ-সময় ঠিক করে।
    ওই সময় পার হলেই public result API নিজে থেকে চালু হয় (আলাদা কোনো job লাগে না)।
    """
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='result_publish_schedules')
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True, related_name='result_publish_schedules',
        help_text="ফাঁকা = ওই exam এর সব সেকশন",
    )
    exam_setup = models.ForeignKey(
        ExamSetup, on_delete=models.CASCADE, null=True, blank=True, related_name='result_publish_schedules',
        help_text="একটা exam এর result প্রকাশ করতে",
    )
    combined_config = models.ForeignKey(
        CombinedResultConfig, on_delete=models.CASCADE, null=True, blank=True,
        related_name='result_publish_schedules', help_text="একাধিক exam মিলানো result প্রকাশ করতে",
    )
    publish_at = models.DateTimeField(help_text="এই তারিখ-সময় থেকে result সবাই দেখতে পাবে")
    is_active = models.BooleanField(default=True, help_text="বন্ধ করলে result প্রকাশ হবে না (আগে প্রকাশ হলেও লুকানো)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_at']
        verbose_name = "Result Publish Schedule"

    def __str__(self):
        target = self.exam_setup or self.combined_config
        return f"{self.academic_class} · {target} · {self.publish_at:%Y-%m-%d %H:%M}"