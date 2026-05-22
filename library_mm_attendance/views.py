from rest_framework import generics, filters, pagination, parsers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.students.models import Student
from library_mm_book_list.models import Book_model
from .models import LibraryAttendance
from .serializers import LibraryAttendanceSerializer, QuickEntrySerializer


class LibraryPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuickEntryView(generics.GenericAPIView):
    serializer_class = QuickEntrySerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def post(self, request, *args, **kwargs):
        roll_number = request.data.get('roll_number')
        book_id = request.data.get('book_id')

        if not roll_number:
            return Response({'error': 'roll_number is required'}, status=400)

        try:
            student = Student.objects.get(roll_number=roll_number)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        # Check if already checked in
        existing = LibraryAttendance.objects.filter(
            student=student,
            date=timezone.now().date(),
            check_out_time__isnull=True
        ).first()

        if existing:
            return Response({'error': 'Student already checked in'}, status=400)

        book = None
        if book_id:
            try:
                book = Book_model.objects.get(id=book_id)
            except Book_model.DoesNotExist:
                return Response({'error': 'Book not found'}, status=404)

        attendance = LibraryAttendance.objects.create(
            student=student,
            book=book,
        )

        serializer = LibraryAttendanceSerializer(attendance)
        return Response(serializer.data, status=201)


class CheckOutView(generics.GenericAPIView):
    serializer_class = LibraryAttendanceSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def patch(self, request, pk, *args, **kwargs):
        try:
            attendance = LibraryAttendance.objects.get(pk=pk)
        except LibraryAttendance.DoesNotExist:
            return Response({'error': 'Attendance not found'}, status=404)

        if attendance.check_out_time:
            return Response({'error': 'Already checked out'}, status=400)

        attendance.check_out_time = timezone.now()
        attendance.save()

        serializer = LibraryAttendanceSerializer(attendance)
        return Response(serializer.data)


class TodayAttendanceView(generics.ListAPIView):
    serializer_class = LibraryAttendanceSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        return LibraryAttendance.objects.filter(
            date=timezone.now().date()
        ).select_related('student', 'book')


class StudentsInLibraryView(generics.ListAPIView):
    serializer_class = LibraryAttendanceSerializer

    def get_queryset(self):
        return LibraryAttendance.objects.filter(
            date=timezone.now().date(),
            check_out_time__isnull=True
        ).select_related('student', 'book')


class HistoricalAttendanceView(generics.ListAPIView):
    serializer_class = LibraryAttendanceSerializer
    pagination_class = LibraryPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']

    def get_queryset(self):
        queryset = LibraryAttendance.objects.all().select_related('student', 'book')

        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        class_name = self.request.query_params.get('class_name')

        if from_date:
            queryset = queryset.filter(date__gte=from_date)
        if to_date:
            queryset = queryset.filter(date__lte=to_date)
        if class_name:
            queryset = queryset.filter(student__class_name_static=class_name)

        return queryset
    


class LibraryAttendanceDestroyView(generics.DestroyAPIView):
    queryset = LibraryAttendance.objects.all().select_related('student', 'book')
    serializer_class = LibraryAttendanceSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]