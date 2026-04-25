from django.db import models
from apps.common.models_audit import AuditModel
from apps.academics.models import AcademicYear, Class, Section, ClassSection

class ExamType(AuditModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(AuditModel):
    # This might eventually move to a global academics subject model
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

class QuestionType(AuditModel):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class QuestionBank(AuditModel):
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.PROTECT, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    question_text = models.TextField()
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    attachment = models.FileField(upload_to='question_bank/', null=True, blank=True)
