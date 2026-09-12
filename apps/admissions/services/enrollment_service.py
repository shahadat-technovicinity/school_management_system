from django.db import transaction
from django.db.models import F
from apps.academics.models import AcademicYear
from apps.students.models import Student, GuardianDetails, AdditionalDetails
from apps.admissions.models import (
    StudentAdmission,
    AdmissionDocument,
    LotterySession,
    PreviousAcademicRecord,
)
from academic_mm_class_and_section.models import Section


@transaction.atomic
def finalize_admission(admission_id, uploaded_files_dict):
    """
    Transfers a 'Selected' admission to a permanent 'Student' profile,
    saves uploaded documents, decrements the class seat count, and marks
    the admission as enrolled.

    Creates:
      - Student (core profile)
      - GuardianDetails (father/mother info from admission)
      - AdditionalDetails (with TC and previous school info)
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

    # 2. Resolve active academic year (fallback to current label)
    active_year = AcademicYear.objects.filter(is_active=True).first()
    academic_year_label = active_year.year_label if active_year else "2025-2026"

    # 2.1 Resolve Section Instance safely
    default_section = Section.objects.filter(name="A").first() or Section.objects.first()

    # 3. Create Core Student Profile
    student_profile = Student.objects.create(
        academic_year=academic_year_label,
        admission_number=f"ADM-{admission.id}",
        admission_date=getattr(admission, 'admission_date', None),
        roll_number=getattr(admission, 'application_number', '') or "",
        status="active",
        first_name=getattr(admission, 'student_name_english', '') or "Student",
        last_name=getattr(admission, 'student_name_bangla', '') or "",
        class_name_static=getattr(admission, 'desired_class', ''),
        section_static=default_section,
        gender=getattr(admission, 'gender', 'male'),
        date_of_birth=getattr(admission, 'date_of_birth', None),
        blood_group="A+",
        religion=getattr(admission, 'religion', 'islam'),
        house="Default House",
        scholarship="f",
        primary_contact_number=getattr(admission, 'mobile_number', '') or "",
    )

    # 4. Create Guardian Details safely (handles missing fields cleanly)
    GuardianDetails.objects.create(
        student=student_profile,
        father_name=getattr(admission, 'father_name_en', '') or 'TBA',
        father_nid_or_birth_certificate=getattr(admission, 'father_nid_number', '') or '',
        mother_name=getattr(admission, 'mother_name_en', '') or 'TBA',
        mother_nid_or_birth_certificate=getattr(admission, 'mother_nid_number', '') or '',
        guardian_type="Parent",
        sibling_studying_same_school=bool(getattr(admission, 'sibling_identification_number', None)),
        sibling_admission_no=getattr(admission, 'sibling_identification_number', '') or '',
    )

    # 5. Create Additional Details with TC and previous school info
    prev_record = getattr(admission, 'previous_academic_record', None)
    AdditionalDetails.objects.create(
        student=student_profile,
        transfer_certificate=uploaded_files_dict.get('tc'),
        previous_school_name=prev_record.school_name if prev_record else "",
        previous_school_address=prev_record.school_address if prev_record else "",
        admission_reference=getattr(admission, 'additional_comments', '') or "",
    )

    # 6. Decrement the configured seat count for this class
    LotterySession.objects.filter(
        target_class__iexact=admission.desired_class
    ).update(total_seats=F('total_seats') - 1)

    # 7. Update Admission Status
    admission.admission_status = 'enrolled'
    admission.save()

    return student_profile


