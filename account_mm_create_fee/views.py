from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CreateFee
from accounts_mm_fee_type.models import FeeHead
from apps.students.models import Student
from .serializers import FeeStructureSerializer, get_leaf_ids, head_info, head_path


class FeeStructureListCreateView(generics.ListCreateAPIView):
    serializer_class = FeeStructureSerializer
    pagination_class = None

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('applies_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="class অথবা student"),
        openapi.Parameter('academic_class', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('fee_head', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('payment_period', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        openapi.Parameter('student', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                          description="এই ছাত্রের জন্য প্রযোজ্য সব fee (class wise + individual)"),
        openapi.Parameter('active_on', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                          description="এই তারিখে চালু আছে এমন fee"),
        openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CreateFee.objects.none()
        qs = CreateFee.objects.select_related('fee_head', 'academic_class').prefetch_related(
            'items__fee_head', 'sections', 'students'
        )
        p = self.request.query_params
        if p.get('applies_to'):
            qs = qs.filter(applies_to=p['applies_to'])
        if p.get('academic_class'):
            qs = qs.filter(academic_class_id=p['academic_class'])
        if p.get('section'):
            qs = qs.filter(Q(sections__id=p['section']) | Q(applies_to='class', sections__isnull=True)).distinct()
        if p.get('fee_head'):
            qs = qs.filter(fee_head_id=p['fee_head'])
        if p.get('payment_period'):
            qs = qs.filter(payment_period=p['payment_period'])
        if p.get('is_active') is not None:
            qs = qs.filter(is_active=p['is_active'].lower() in ('1', 'true', 'yes'))
        if p.get('active_on'):
            qs = qs.filter(valid_from__lte=p['active_on'], valid_until__gte=p['active_on'])
        if p.get('student'):
            student = Student.objects.filter(id=p['student']).first()
            if not student:
                return qs.none()
            by_class = Q(applies_to='class', academic_class_id=student.class_name_static_id) & (
                Q(sections__isnull=True) | Q(sections__id=student.section_static_id)
            )
            qs = qs.filter(Q(applies_to='student', students__id=student.id) | by_class).distinct()
        return qs


class FeeStructureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CreateFee.objects.select_related('fee_head', 'academic_class').prefetch_related(
        'items__fee_head', 'sections', 'students'
    )
    serializer_class = FeeStructureSerializer


class FeeFormItemsView(APIView):
    """
    Fee Type বাছার পর form এ কোন কোন fee এর টাকা দিতে হবে তার তালিকা।
    নিচে sub category থাকলে সেগুলো আসে, না থাকলে Fee Type নিজেই একটা item।
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('fee_head', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
    ])
    def get(self, request):
        head_id = request.query_params.get('fee_head')
        if not head_id:
            return Response({'error': 'fee_head দিতে হবে।'}, status=status.HTTP_400_BAD_REQUEST)
        head = FeeHead.objects.filter(id=head_id).first()
        if not head:
            return Response({'error': 'Fee Type পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        info, children = head_info()
        leaf_ids = get_leaf_ids(head.id, info, children)
        return Response({
            'fee_head': head.id,
            'name': head.name,
            'has_children': bool(children.get(head.id)),
            'items': [
                {'fee_head': i, 'name': info[i]['name'], 'path': head_path(i, info)}
                for i in leaf_ids
            ],
        })


class StudentPickerView(APIView):
    """Individual fee এর জন্য ছাত্র বাছতে। class/section/নাম দিয়ে খোঁজা যায়।"""

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description="নাম, roll বা admission number"),
    ])
    def get(self, request):
        p = request.query_params
        qs = Student.objects.select_related('class_name_static', 'section_static')
        if p.get('class_id'):
            qs = qs.filter(class_name_static_id=p['class_id'])
        if p.get('section_id'):
            qs = qs.filter(section_static_id=p['section_id'])
        if p.get('search'):
            s = p['search']
            qs = qs.filter(
                Q(first_name__icontains=s) | Q(last_name__icontains=s)
                | Q(roll_number__icontains=s) | Q(admission_number__icontains=s)
            )
        qs = qs.order_by('class_name_static_id', 'section_static__name', 'roll_number')[:200]
        return Response([
            {
                'id': st.id,
                'name': getattr(st, 'full_name', str(st)),
                'roll_number': st.roll_number,
                'admission_number': st.admission_number,
                'class': st.class_name_static.name if st.class_name_static else '',
                'section': st.section_static.name if st.section_static else '',
            }
            for st in qs
        ])