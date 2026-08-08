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

    # 3. Create Core Student Profile
    student_profile = Student.objects.create(
        academic_year=academic_year_label,
        admission_number=f"ADM-{admission.id}",
        admission_date=admission.admission_date,
        roll_number=admission.application_number or "",
        status="active",
        first_name=admission.student_name_english,
        last_name=admission.student_name_bangla or "",
        class_name_static=admission.desired_class,
        section_static="A",
        gender=admission.gender,
        date_of_birth=admission.date_of_birth,
        blood_group="A+",
        religion=admission.religion,
        house="Default House",
        scholarship="f",
        primary_contact_number=admission.mobile_number,
    )

    # 4. Create Guardian Details from admission parent info
    present_address = (
        f"{admission.present_address_village}, "
        f"{admission.present_address_post_office}, "
        f"{admission.present_address_sub_district}, "
        f"{admission.present_address_district}"
    )
    permanent_address = ""
    if not admission.is_permanent_same_as_present:
        permanent_address = (
            f"{admission.permanent_address_village}, "
            f"{admission.permanent_address_post_office}, "
            f"{admission.permanent_address_sub_district}, "
            f"{admission.permanent_address_district}"
        )

    GuardianDetails.objects.create(
        student=student_profile,
        father_name=admission.father_name_en,
        father_nid_or_birth_certificate=admission.father_nid_number,
        mother_name=admission.mother_name_en,
        mother_nid_or_birth_certificate=admission.mother_nid_number,
        guardian_type="Parent",
        sibling_studying_same_school=bool(admission.sibling_identification_number),
        sibling_admission_no=admission.sibling_identification_number or "",
        current_address=present_address,
        permanent_address=permanent_address,
    )

    # 5. Create Additional Details with TC and previous school info
    prev_record = getattr(admission, 'previous_academic_record', None)
    AdditionalDetails.objects.create(
        student=student_profile,
        transfer_certificate=uploaded_files_dict.get('tc'),
        previous_school_name=prev_record.school_name if prev_record else "",
        previous_school_address=prev_record.school_address if prev_record else "",
        admission_reference=admission.additional_comments or "",
    )

    # 6. Decrement the configured seat count for this class
    LotterySession.objects.filter(
        target_class__iexact=admission.desired_class
    ).update(total_seats=F('total_seats') - 1)

    # 7. Update Admission Status
    admission.admission_status = 'enrolled'
    admission.save()

    return student_profile
