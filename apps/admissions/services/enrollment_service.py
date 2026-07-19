from django.db import transaction
from django.db.models import F
from apps.students.models import Student
from apps.admissions.models import StudentAdmission, AdmissionDocument, LotterySession


@transaction.atomic
def finalize_admission(admission_id, uploaded_files_dict):
    """
    Transfers a 'Selected' admission to a permanent 'Student' profile,
    saves uploaded documents, decrements the class seat count, and marks
    the admission as enrolled.
    """
    admission = StudentAdmission.objects.get(id=admission_id)

    if admission.admission_status != 'selected':
        raise ValueError("Only 'Selected' applicants can be finalized.")

    # 1. Save uploaded documents
    for doc_type, file_obj in uploaded_files_dict.items():
        AdmissionDocument.objects.create(
            admission=admission,
            document_type=doc_type,
            file=file_obj
        )

    # 2. Transfer data to Core Profile (student_profile.Student)
    student_profile = Student.objects.create(
        academic_year="2025-2026",
        admission_number=f"ADM-{admission.id}",
        admission_date=admission.admission_date,
        status="active",
        first_name=admission.student_name_english,
        last_name="",
        # Model stores class/section in *_static fields (db columns class_name / section)
        class_name_static=admission.desired_class,
        section_static="A",
        gender=admission.gender,
        date_of_birth=admission.date_of_birth,
        blood_group="A+",
        religion=admission.religion,
        scholarship="f",
        primary_contact_number=admission.mobile_number,
        house="Default House",
    )

    # 3. Decrement the configured seat count for this class
    LotterySession.objects.filter(
        target_class__iexact=admission.desired_class
    ).update(total_seats=F('total_seats') - 1)

    # 4. Update Admission Status
    admission.admission_status = 'enrolled'
    admission.save()

    return student_profile