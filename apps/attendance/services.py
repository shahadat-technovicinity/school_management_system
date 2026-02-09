from django.db import transaction
from apps.attendance.models import Attendance

@transaction.atomic
def bulk_mark_attendance(class_section, date, records, teacher):
    objs = []
    for r in records:
        objs.append(
            Attendance(
                student_id=r['student'],
                class_section=class_section,
                date=date,
                status=r['status'],
                marked_by=teacher
            )
        )
    Attendance.objects.bulk_create(objs, ignore_conflicts=True)
