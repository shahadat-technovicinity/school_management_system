import secrets
from django.db import transaction
from apps.admissions.models import StudentAdmission, LotterySession

def assign_sequential_numbers(class_name):
    """
    Assigns sequential admin numbers to approved applicants before a lottery spin.
    """
    applicants = StudentAdmission.objects.filter(
        desired_class=class_name, admission_status='pending'
    ).order_by('admission_date')
    
    assigned_count = 0
    for i, applicant in enumerate(applicants, start=1):
        applicant.admin_form_number = f"ADM-2025-{i:04d}"
        applicant.save(update_fields=['admin_form_number'])
        assigned_count += 1
    return assigned_count

@transaction.atomic
def execute_lottery(class_name, num_seats):
    """
    Cryptographically secure random selection among pending applicants.
    """
    pending = list(StudentAdmission.objects.filter(
        desired_class=class_name, admission_status='pending', admin_form_number__isnull=False
    ).values_list('id', flat=True))
    
    if num_seats >= len(pending):
        winners = pending
    else:
        # Cryptographic fairness
        winners = set()
        while len(winners) < num_seats:
            winners.add(secrets.choice(pending))
        winners = list(winners)
        
    # Block update database
    StudentAdmission.objects.filter(id__in=winners).update(admission_status='selected')
    
    return len(winners)
