import csv
import io
from apps.admissions.models import StudentAdmission

def import_students_from_csv(file_obj, class_name, section):
    """
    Parses a CSV file and bulk inserts StudentAdmission records.
    Assumes standard columns: name_en, name_bn, dob, gender, mobile, birth_reg
    """
    decoded_file = file_obj.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    admissions_to_create = []
    
    for count, row in enumerate(reader, start=1):
        # In a real app, validate row fields here
        admission = StudentAdmission(
            desired_class=class_name,
            student_name_english=row.get('name_en', f'Student {count}'),
            student_name_bangla=row.get('name_bn', ''),
            date_of_birth=row.get('dob', '2015-01-01'),
            gender=row.get('gender', 'male').lower(),
            mobile_number=row.get('mobile', '00000000000'),
            birth_registration_number=row.get('birth_reg', f'BRN-TEMP-{count}'),
            admission_status='pending',
            # Apply missing required defaults
            religion='islam', 
            father_name_en='TBA',
            father_name_bn='TBA',
            father_nid_number=f'NID-T-{count}',
            mother_name_en='TBA',
            mother_name_bn='TBA',
            mother_nid_number=f'NID-M-{count}'
        )
        admissions_to_create.append(admission)
        
    # Bulk insert for fast execution
    StudentAdmission.objects.bulk_create(admissions_to_create)
    return len(admissions_to_create)
