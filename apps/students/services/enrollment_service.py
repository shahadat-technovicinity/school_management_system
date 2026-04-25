from django.db import transaction
from apps.students.models import Student, GuardianDetails, AdditionalDetails

class EnrollmentService:
    @staticmethod
    @transaction.atomic
    def enroll_new_student(student_data, guardian_data=None, additional_data=None):
        """
        Handles the complex logic of enrolling a new student, 
        ensuring all related records (Guardian, Medical, etc.) are created together.
        """
        # Create Student
        student = Student.objects.create(**student_data)
        
        # Create Guardian Details
        if guardian_data:
            GuardianDetails.objects.create(student=student, **guardian_data)
            
        # Create Additional/Medical Details
        if additional_data:
            AdditionalDetails.objects.create(student=student, **additional_data)
            
        return student

    @staticmethod
    def get_student_360_profile(student_id):
        """
        Aggregates data for the Student Profile dashboard across different modules.
        (Attendance, Exam Results, etc.)
        """
        try:
            student = Student.objects.prefetch_related('guardian_info', 'additional_info').get(id=student_id)
            # Future: add logic here to fetch attendance percentage, latest marks, etc.
            return student
        except Student.DoesNotExist:
            return None
