from django.db import transaction, models
from django.db.models import F
from apps.students.models import Student
from apps.admissions.models import StudentAdmission, AdmissionDocument, LotterySession


@transaction.atomic
def finalize_admission(admission_id, uploaded_files_dict):
    admission = StudentAdmission.objects.get(id=admission_id)
    if admission.admission_status != 'selected':
        raise ValueError("Only 'Selected' applicants can be finalized.")

    for doc_type, file_obj in uploaded_files_dict.items():
        AdmissionDocument.objects.create(
            admission=admission,
            document_type=doc_type,
            file=file_obj
        )

    student_profile = Student.objects.create(
        academic_year="2025-2026",
        admission_number=f"ADM-{admission.id}",
        admission_date=admission.admission_date,
        status="active",
        first_name=admission.student_name_english,
        last_name="",
        class_name=admission.desired_class,
        section="section A",
        gender=admission.gender,
        date_of_birth=admission.date_of_birth,
        blood_group="A+",
        religion=admission.religion,
        primary_contact_number=admission.mobile_number,
        house="Default House"
    )

    LotterySession.objects.filter(
        target_class__iexact=admission.desired_class
    ).update(total_seats=F('total_seats') - 1)

    admission.admission_status = 'enrolled'
    admission.save()
    return student_profile