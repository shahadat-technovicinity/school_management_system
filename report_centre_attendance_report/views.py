from rest_framework import generics
from rest_framework.response import Response
from datetime import date as today_date
from apps.attendance.models import Attendance
from academic_class_routine.models import ClassRoutine
from .serializers import AttendanceReportSerializer


class AttendanceReportView(generics.GenericAPIView):
    serializer_class = AttendanceReportSerializer

    def get(self, request, *args, **kwargs):
        class_section_id = request.query_params.get('class_section')
        report_date = request.query_params.get('date', str(today_date.today()))

        queryset = Attendance.objects.filter(
            date=report_date
        ).select_related('student', 'class_section', 'marked_by')

        if class_section_id:
            queryset = queryset.filter(class_section_id=class_section_id)

        total = queryset.count()
        present = queryset.filter(status='P').count()
        absent = queryset.filter(status='A').count()

        students = []
        for att in queryset:
            # ClassRoutine থেকে time নাও
            routine = ClassRoutine.objects.filter(
                class_name=att.class_section.class_name,
                section=att.class_section.section,
            ).first()

            students.append({
                'student_id': att.student.admission_number,
                'name': att.student.full_name,
                'class': att.class_section.class_name if att.class_section else '',
                'section': att.class_section.section if att.class_section else '',
                'status': 'Present' if att.status == 'P' else 'Absent',
                'time_in': str(routine.start_time) if routine else '-',
                'time_out': str(routine.end_time) if routine else '-',
            })

        return Response({
            'date': report_date,
            'summary': {
                'total_students': total,
                'present': present,
                'absent': absent,
                'present_percentage': round((present / total) * 100, 1) if total else 0,
                'absent_percentage': round((absent / total) * 100, 1) if total else 0,
            },
            'students': students,
        })