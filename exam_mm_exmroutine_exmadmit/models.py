from django.db import models
from academic_mm_class_and_section.models import AcademicClass
from academic_create_subject.models import Subject_Name
from exam_mm_exam_setup.models import ExamName, ExamSetup


class ExamRoutine(models.Model):
    exam_name = models.ForeignKey(
        ExamName, 
        on_delete=models.CASCADE, 
        related_name='exam_routinesss'
    )
    
    academic_class = models.ForeignKey(
        AcademicClass, 
        on_delete=models.CASCADE, 
        related_name='exam_routiness'
    )

    exam_setup = models.ForeignKey(
        ExamSetup,
        on_delete=models.CASCADE,
        related_name='exam_routines',
        null=True,
        blank=True,
        help_text="Automated reference to the configured exam setup"
    )

    # Dynamic subject
    subject = models.ForeignKey(
        Subject_Name, 
        on_delete=models.CASCADE,
        related_name='exam_routiness'
    )

    exam_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="Exam start time (e.g. 10:00:00)")
    end_time = models.TimeField(null=True, blank=True, help_text="Exam end time (e.g. 13:00:00)")
    total_marks = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Exam full mark (e.g. 100.00)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exam_date', 'start_time', 'id']

    def save(self, *args, **kwargs):
        setup = ExamSetup.objects.filter(
            exam_name=self.exam_name,
            academic_class=self.academic_class
        ).first()
        if setup:
            self.exam_setup = setup
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.exam_name.name} - {self.academic_class.name} - {self.subject.name} ({self.exam_date})"