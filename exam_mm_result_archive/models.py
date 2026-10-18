from django.db import models
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from exam_mm_exmroutine_exmadmit.models import ExamsRoutine


def calculate_grade_and_gpa(percentage):
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
            return self.exam_routine.academic_class.id in [4, 5]
        except Exception:
            return False


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

        # Class 6-8 এ practical marks 0 করে দাও
        if not config.has_practical:
            self.practical_marks = 0

        # Total Marks
        self.total_marks = self.written_marks + self.mcq_marks + self.practical_marks

        # Full Marks
        full_marks = float(config.written_full_marks) + float(config.mcq_full_marks)
        if config.has_practical:
            full_marks += float(config.practical_full_marks)

        # Percentage
        percentage = (float(self.total_marks) / full_marks) * 100 if full_marks > 0 else 0

        # Grade & GPA
        self.grade, gpa = calculate_grade_and_gpa(percentage)
        self.gpa = gpa

        # Written Pass/Fail
        self.written_status = 'pass' if self.written_marks >= config.written_pass_marks else 'fail'

        # MCQ Pass/Fail
        self.mcq_status = 'pass' if self.mcq_marks >= config.mcq_pass_marks else 'fail'

        # Practical Pass/Fail
        if config.has_practical:
            self.practical_status = 'pass' if self.practical_marks >= config.practical_pass_marks else 'fail'
        else:
            self.practical_status = 'pass'

        # Overall Pass/Fail
        statuses = [self.written_status, self.mcq_status]
        if config.has_practical:
            statuses.append(self.practical_status)

        self.overall_status = 'pass' if all(s == 'pass' for s in statuses) and self.grade != 'F' else 'fail'

    def save(self, *args, **kwargs):
        self.calculate_result()
        super().save(*args, **kwargs)