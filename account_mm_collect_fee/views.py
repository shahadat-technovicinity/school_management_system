from rest_framework import generics, filters, pagination, parsers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.students.models import Student
from account_mm_create_fee.models import CreateFee
from account_mm_std_stipent.models import stipend_student, stipend_free_hf
from .models import FeeCollection, FeeCollectionItem
from .serializers import FeeCollectionSerializer, OutstandingFeeSerializer


class FeePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class StudentFeeSearchView(generics.GenericAPIView):
    serializer_class = OutstandingFeeSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student_id',
                openapi.IN_QUERY,
                description="Student ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student_id')

        if not student_id:
            return Response({'error': 'student_id is required'}, status=400)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        today = timezone.now().date()

        # Class wise fee
        class_fees = CreateFee.objects.filter(
            select_class=student.class_name_static
        )

        # Stipend
        stipend = stipend_student.objects.filter(
            student_id=str(student.id),
            status='Active',
            start_date__lte=today,
            end_date__gte=today,
        ).first()
        stipend_amount = float(stipend.amount) if stipend else 0

        # Concession
        concession = stipend_free_hf.objects.filter(
            student_id=str(student.id),
            status='Active',
            valid_till__gte=today,
        ).first()
        concession_amount = float(concession.concession_ammount) if concession else 0

        # Outstanding fees
        outstanding = []
        total_amount = 0

        for fee in class_fees:
            # Already paid check
            already_paid = FeeCollectionItem.objects.filter(
                fee=fee,
                collection__student=student,
                collection__status='paid'
            ).exists()

            if not already_paid:
                outstanding.append({
                    'fee_id': fee.id,
                    'fee_type': fee.fee_type,
                    'amount': float(fee.amount),
                    'due_date': fee.due_date,
                    'status': 'due',
                })
                total_amount += float(fee.amount)

        discount = stipend_amount + concession_amount
        final_amount = total_amount - discount

        return Response({
            'student': {
                'id': student.id,
                'admission_number': student.admission_number,
                'name': student.full_name,
                'class': student.class_name_static,
                'section': student.section_static,
                'scholarship': student.scholarship,
            },
            'outstanding_fees': outstanding,
            'summary': {
                'total_amount': total_amount,
                'stipend_discount': stipend_amount,
                'concession_discount': concession_amount,
                'total_discount': discount,
                'final_amount': final_amount,
            }
        })


class FeeCollectionListCreateView(generics.ListCreateAPIView):
    serializer_class = FeeCollectionSerializer
    pagination_class = FeePagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__first_name', 'student__last_name', 'status']

    def get_queryset(self):
        queryset = FeeCollection.objects.all().select_related('student')

        class_name = self.request.query_params.get('class_name')
        status_filter = self.request.query_params.get('status')
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        method = self.request.query_params.get('method')

        if class_name:
            queryset = queryset.filter(student__class_name_static=class_name)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if from_date:
            queryset = queryset.filter(payment_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(payment_date__lte=to_date)
        if method:
            queryset = queryset.filter(payment_method=method)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        try:
            student = Student.objects.get(id=data.get('student'))
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=400)

        today = timezone.now().date()

        # Stipend
        stipend = stipend_student.objects.filter(
            student_id=str(student.id),
            status='Active',
            start_date__lte=today,
            end_date__gte=today,
        ).first()
        stipend_amount = float(stipend.amount) if stipend else 0

        # Concession
        concession = stipend_free_hf.objects.filter(
            student_id=str(student.id),
            status='Active',
            valid_till__gte=today,
        ).first()
        concession_amount = float(concession.concession_ammount) if concession else 0

        # Class wise fee
        class_fees = CreateFee.objects.filter(
            select_class=student.class_name_static
        )

        total_amount = 0
        fee_items = []

        for fee in class_fees:
            already_paid = FeeCollectionItem.objects.filter(
                fee=fee,
                collection__student=student,
                collection__status='paid'
            ).exists()

            if not already_paid:
                total_amount += float(fee.amount)
                fee_items.append(fee)

        discount = stipend_amount + concession_amount
        final_amount = total_amount - discount

        # FeeCollection save
        collection = FeeCollection.objects.create(
            student=student,
            total_amount=total_amount,
            discount_amount=discount,
            final_amount=final_amount,
            payment_method=data.get('payment_method'),
            transaction_id=data.get('transaction_id'),
            payment_date=data.get('payment_date'),
            notes=data.get('notes', ''),
            status='paid',
        )

        # FeeCollectionItem save
        for fee in fee_items:
            FeeCollectionItem.objects.create(
                collection=collection,
                fee=fee,
                amount=fee.amount,
            )

        serializer = self.get_serializer(collection)
        return Response(serializer.data, status=201)


class FeeCollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeeCollection.objects.all().select_related('student')
    serializer_class = FeeCollectionSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]