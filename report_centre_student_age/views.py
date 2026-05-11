from rest_framework import generics
from rest_framework.response import Response
from datetime import date
from apps.students.models import Student
from .serializers import StudentAgeDistributionSerializer


class StudentAgeDistributionReportView(generics.GenericAPIView):
    serializer_class = StudentAgeDistributionSerializer

    def get(self, request, *args, **kwargs):
        academic_year = request.query_params.get('academic_year')
        class_name = request.query_params.get('class_name')

        queryset = Student.objects.filter(status='active')

        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        if class_name:
            queryset = queryset.filter(class_name_static=class_name)

        today = date.today()
        age_data = {}
        total_students = 0
        total_male = 0
        total_female = 0
        age_list = []

        for student in queryset:
            if not student.date_of_birth:
                continue

            age = today.year - student.date_of_birth.year - (
                (today.month, today.day) < (student.date_of_birth.month, student.date_of_birth.day)
            )
            class_key = student.class_name_static or 'Unknown'

            if class_key not in age_data:
                age_data[class_key] = {}

            age_key = str(age)
            if age_key not in age_data[class_key]:
                age_data[class_key][age_key] = {'total': 0, 'male': 0, 'female': 0}

            age_data[class_key][age_key]['total'] += 1
            total_students += 1
            age_list.append(age)

            if student.gender == 'male':
                age_data[class_key][age_key]['male'] += 1
                total_male += 1
            elif student.gender == 'female':
                age_data[class_key][age_key]['female'] += 1
                total_female += 1

        average_age = round(sum(age_list) / len(age_list), 1) if age_list else 0
        most_common_age = max(set(age_list), key=age_list.count) if age_list else 0

        return Response({
            'age_distribution': age_data,
            'summary': {
                'total_students': total_students,
                'total_male': total_male,
                'total_female': total_female,
                'male_percentage': round((total_male / total_students) * 100, 1) if total_students else 0,
                'female_percentage': round((total_female / total_students) * 100, 1) if total_students else 0,
                'average_age': average_age,
                'most_common_age': most_common_age,
            }
        })