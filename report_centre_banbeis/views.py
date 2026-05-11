from rest_framework import generics
from rest_framework.response import Response
from apps.students.models import Student
from teacher_mm_teacher.models import Teacher
from .serializers import EnrollmentDataSerializer, TeacherInfoSerializer


class BANBEISEnrollmentView(generics.GenericAPIView):
    serializer_class = EnrollmentDataSerializer

    def get(self, request, *args, **kwargs):
        academic_year = request.query_params.get('academic_year')

        students = Student.objects.filter(status='active')
        if academic_year:
            students = students.filter(academic_year=academic_year)

        total = students.count()
        male = students.filter(gender='male').count()
        female = students.filter(gender='female').count()
        gender_ratio = round(male / female, 2) if female > 0 else 0

        # Class wise breakdown
        class_wise = []
        for class_name in ['class 6', 'class 7', 'class 8', 'class 9', 'class 10']:
            class_students = students.filter(class_name_static=class_name)
            class_total = class_students.count()
            class_male = class_students.filter(gender='male').count()
            class_female = class_students.filter(gender='female').count()

            class_wise.append({
                'class': class_name,
                'total_students': class_total,
                'male': class_male,
                'female': class_female,
                'gender_ratio': round(class_male / class_female, 2) if class_female > 0 else 0,
            })

        return Response({
            'stats': {
                'total_students': total,
                'male_students': male,
                'female_students': female,
                'gender_ratio': gender_ratio,
            },
            'class_wise': class_wise,
        })


class BANBEISTeacherInfoView(generics.GenericAPIView):
    serializer_class = TeacherInfoSerializer

    def get(self, request, *args, **kwargs):
        teachers = Teacher.objects.filter(status='active')

        total = teachers.count()
        male = teachers.filter(gender='male').count()
        female = teachers.filter(gender='female').count()

        # Qualification breakdown
        qualifications = {}
        for teacher in teachers:
            qual = teacher.qualification or 'Unknown'
            if qual not in qualifications:
                qualifications[qual] = {
                    'total': 0,
                    'male': 0,
                    'female': 0,
                }
            qualifications[qual]['total'] += 1
            if teacher.gender == 'male':
                qualifications[qual]['male'] += 1
            elif teacher.gender == 'female':
                qualifications[qual]['female'] += 1

        qual_list = [
            {
                'qualification': k,
                'total': v['total'],
                'male': v['male'],
                'female': v['female'],
            }
            for k, v in qualifications.items()
        ]

        return Response({
            'stats': {
                'total_teachers': total,
                'male_teachers': male,
                'female_teachers': female,
            },
            'qualification_breakdown': qual_list,
        })