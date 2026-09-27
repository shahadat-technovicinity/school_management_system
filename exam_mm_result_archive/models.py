from django.db import models
from apps.students.models import Student


class SubjectPassMarkConfig(models.Model):
    academic_class = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=100)
    
    writing_full_mark = models.FloatField(default=0)
    writing_pass_mark = models.FloatField(default=0)
    
    mcq_full_mark = models.FloatField(default=0)
    mcq_pass_mark = models.FloatField(default=0)
    
    practical_full_mark = models.FloatField(default=0)
    practical_pass_mark = models.FloatField(default=0)
    
    total_full_mark = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.total_full_mark = self.writing_full_mark + self.mcq_full_mark + self.practical_full_mark
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.academic_class} - {self.subject} ({self.exam_type})"


class GradeScale(models.Model):
    academic_class = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    letter_grade = models.CharField(max_length=5)
    grade_point = models.FloatField()
    min_mark = models.FloatField()
    max_mark = models.FloatField()

    def __str__(self):
        return f"{self.letter_grade} ({self.grade_point}) : {self.min_mark}-{self.max_mark}"


class ExamMark(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_marks')
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=100)
    
    writing = models.FloatField(default=0)
    mcq = models.FloatField(default=0)
    practical = models.FloatField(default=0)
    total = models.FloatField(default=0)
    
    grade_point = models.FloatField(default=0.0)
    letter_grade = models.CharField(max_length=5, default='F')
    is_passed = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total = self.writing + self.mcq + self.practical
        
        # Section-wise pass mark checking
        config = SubjectPassMarkConfig.objects.filter(
            subject=self.subject,
            exam_type=self.exam_type
        ).first()

        is_writing_pass = True
        is_mcq_pass = True
        is_practical_pass = True

        if config:
            if config.writing_pass_mark > 0 and self.writing < config.writing_pass_mark:
                is_writing_pass = False
            if config.mcq_pass_mark > 0 and self.mcq < config.mcq_pass_mark:
                is_mcq_pass = False
            if config.practical_pass_mark > 0 and self.practical < config.practical_pass_mark:
                is_practical_pass = False

        if is_writing_pass and is_mcq_pass and is_practical_pass and self.total >= 33:
            self.is_passed = True
            
            # Grade Scale Calculation
            grades = GradeScale.objects.all().order_by('-min_mark')
            matched = False
            for g in grades:
                if g.min_mark <= self.total <= g.max_mark:
                    self.letter_grade = g.letter_grade
                    self.grade_point = g.grade_point
                    matched = True
                    break
            
            if not matched:
                self.letter_grade = 'D'
                self.grade_point = 1.0
        else:
            self.is_passed = False
            self.letter_grade = 'F'
            self.grade_point = 0.0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.subject} - {self.total}"