from django.db import models
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from academic_create_subject.models import Subject_Name
from exam_mm_exam_setup.models import ExamName


class SubjectPassMarkConfig(models.Model):
    academic_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name="pass_configs")
    subject = models.ForeignKey(Subject_Name, on_delete=models.CASCADE, related_name="pass_configs")
    exam_type = models.ForeignKey(ExamName, on_delete=models.CASCADE, related_name="pass_configs")

    # Full & Pass Marks Criteria
    writing_full_mark = models.FloatField(default=0)
    writing_pass_mark = models.FloatField(default=0)

    mcq_full_mark = models.FloatField(default=0)
    mcq_pass_mark = models.FloatField(default=0)

    practical_full_mark = models.FloatField(default=0)
    practical_pass_mark = models.FloatField(default=0)

    total_full_mark = models.FloatField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('academic_class', 'subject', 'exam_type')

    def save(self, *args, **kwargs):
        self.total_full_mark = (self.writing_full_mark or 0) + (self.mcq_full_mark or 0) + (self.practical_full_mark or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_class} - {self.subject} ({self.exam_type})"


class GradeScale(models.Model):
    letter_grade = models.CharField(max_length=5, unique=True)  # A+, A, A-, B, C, D, F
    grade_point = models.FloatField()                          # 5.0, 4.0, 3.5, 3.0, 2.0, 1.0, 0.0
    min_mark = models.FloatField()                             # e.g., 80.0
    max_mark = models.FloatField()                             # e.g., 100.0

    class Meta:
        ordering = ['-grade_point']

    def __str__(self):
        return f"{self.letter_grade} ({self.grade_point}) [{self.min_mark}-{self.max_mark}]"


class ExamMark(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_marks')
    subject = models.ForeignKey(Subject_Name, on_delete=models.CASCADE, related_name="resultarchive")
    exam_type = models.ForeignKey(ExamName, on_delete=models.CASCADE, related_name="exam_marks")

    writing = models.FloatField(default=0)
    mcq = models.FloatField(default=0)
    practical = models.FloatField(default=0)

    total = models.FloatField(default=0, editable=False)
    grade_point = models.FloatField(default=0.0, editable=False)
    letter_grade = models.CharField(max_length=5, default="F", editable=False)
    is_passed = models.BooleanField(default=False, editable=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam_type')

    def save(self, *args, **kwargs):
        self.total = (self.writing or 0) + (self.mcq or 0) + (self.practical or 0)

        # Auto Calculate Pass/Fail & GPA from config if available
        config = SubjectPassMarkConfig.objects.filter(
            academic_class=self.student.class_name_static,
            subject=self.subject,
            exam_type=self.exam_type
        ).first()

        if config:
            pass_writing = self.writing >= config.writing_pass_mark if config.writing_full_mark > 0 else True
            pass_mcq = self.mcq >= config.mcq_pass_mark if config.mcq_full_mark > 0 else True
            pass_practical = self.practical >= config.practical_pass_mark if config.practical_full_mark > 0 else True

            self.is_passed = pass_writing and pass_mcq and pass_practical
        else:
            self.is_passed = self.total >= 33.0

        # Calculate Letter Grade
        if self.is_passed:
            grade_obj = GradeScale.objects.filter(min_mark__lte=self.total, max_mark__gte=self.total).first()
            if grade_obj:
                self.grade_point = grade_obj.grade_point
                self.letter_grade = grade_obj.letter_grade
            else:
                self.grade_point = 0.0
                self.letter_grade = "F"
        else:
            self.grade_point = 0.0
            self.letter_grade = "F"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.exam_type})"