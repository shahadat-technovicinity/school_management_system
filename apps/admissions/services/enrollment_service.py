from django.db import transaction
from student_profile.models import StudentPersonalInfo
from apps.admissions.models import StudentAdmission, AdmissionDocument

@transaction.atomic
def finalize_admission(admission_id, uploaded_files_dict):
    """
    Transfers a 'Selected' admission to a permanent 'StudentPersonalInfo' profile
    and saves uploaded documents.
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

    # 2. Transfer data to Core Profile (student_profile.StudentPersonalInfo)
    # Mapping based on StudentPersonalInfo fields seen earlier
    student_profile = StudentPersonalInfo.objects.create(
        academic_year="2025-2026", # Example mapping
        admission_number=f"ADM-{admission.id}",
        admission_date=admission.admission_date,
        status="active",
        first_name=admission.student_name_english,
        last_name="",
        class_name=admission.desired_class,
        section="section A", # Need dynamic linking in full version
        gender=admission.gender,
        date_of_birth=admission.date_of_birth,
        blood_group="A+", # Mock mapped
        religion=admission.religion,
        primary_contact_number=admission.mobile_number,
        house="Default House"
    )

    # 3. Update Admission Status
    admission.admission_status = 'enrolled'
    admission.save()

    return student_profile
