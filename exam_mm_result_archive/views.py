from rest_framework import generics, status
from student_profile.models import StudentPersonalInfo
from rest_framework.response import Response
from .models import *
from .serializers import *


class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer

    def get_queryset(self):
        queryset = StudentPersonalInfo.objects.all()
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)

        return queryset.order_by('roll_number')


class MarksListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExamMark.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MarkSubmissionSerializer
        return MarksSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save()
        return Response(response_data, status=status.HTTP_201_CREATED)


##student mark and total view
class FinalResultView(generics.ListAPIView):
    serializer_class = FinalResultSerializer

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return StudentPersonalInfo.objects.none()

        queryset = StudentPersonalInfo.objects.all()

        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        exam_type = self.request.query_params.get('exam_type')

        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)

        self.exam_type = exam_type

        return queryset

    def get_serializer_context(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            context = super().get_serializer_context()
            context['exam_type'] = None
            return context

        context = super().get_serializer_context()
        context['exam_type'] = getattr(self, 'exam_type', None)
        return context


class MarkRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarksSerializer




