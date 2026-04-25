from django.db import models
from apps.common.models_audit import AuditModel
from apps.academics.models import AcademicYear, Class, Section, ClassSection
from teacher_mm_teacher.models import Teacher  # Adjusted based on initial structure
from django.core.validators import MinValueValidator, MaxValueValidator

class ExamType(AuditModel):
    name = models.CharField(max_length=100)  # e.g., Midterm, Final, Quiz
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(AuditModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name

class ExamSetup(AuditModel):
    title = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    pass_marks = models.DecimalField(max_digits=5, decimal_places=2, default=33.00)
    exam_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.class_name}"

class ExamRoutine(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE, related_name='routines')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        unique_together = ('exam_setup', 'class_section')

class ExamAdmitCard(AuditModel):
    # This might be more of a generated state/link, but we can track metadata
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)

class ExamSeatPlan(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50)
    seat_number = models.CharField(max_length=20)

class TeacherDuty(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50)
    duty_start_time = models.TimeField()
    duty_end_time = models.TimeField()

class QuestionBank(AuditModel):
    QUESTION_TYPES = [
        ('short', 'Short Answer'),
        ('mcq', 'MCQ'),
        ('long', 'Long Answer'),
    ]
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question_type = models.ForeignKey('QuestionType', on_delete=models.PROTECT, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    question_text = models.TextField()
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    attachment = models.FileField(upload_to='question_bank/', null=True, blank=True)

class QuestionType(AuditModel):
    name = models.CharField(max_length=50) # MCQ, Short, etc.
    def __str__(self): return self.name

class StudentResult(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        unique_together = ('exam_setup', 'student')
