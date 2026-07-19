from rest_framework import generics, status, filters, pagination, parsers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SMSTemplate, SMSSentHistory
from communication_canter_sms_template.serializers import SMSTemplateSerializer
from .serializers import (
    SMSSentHistorySerializer,
    SendSMSSerializer,
    SMSStatsSerializer,
)
from .tasks import send_bulk_sms_task
from .utils import get_balance, get_report

User = get_user_model()


def get_phone_numbers(group):
    from apps.students.models import Student
    from apps.students.models import GuardianDetails

    numbers = []

    if group == 'all_teachers':
        numbers = list(User.objects.filter(role__name='Teacher').values_list('phone_number', flat=True))
    elif group == 'all_staff':
        numbers = list(User.objects.filter(role__name='Staff').values_list('phone_number', flat=True))
    elif group == 'all_students':
        numbers = list(Student.objects.values_list('primary_contact_number', flat=True))
    elif group == 'all_parents':
        guardians = GuardianDetails.objects.all()
        for g in guardians:
            if g.father_phone:
                numbers.append(g.father_phone)
            if g.mother_phone:
                numbers.append(g.mother_phone)
    elif group.startswith('class_'):
        class_name = group.replace('_', ' ')
        numbers = list(Student.objects.filter(
            class_name_static=class_name
        ).values_list('primary_contact_number', flat=True))

    return [n for n in numbers if n]


class SMSTemplatePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class SMSTemplateListCreateView(generics.ListCreateAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    pagination_class = SMSTemplatePagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['template_name', 'category', 'template_content']


class SMSTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class SendSMSView(generics.CreateAPIView):
    serializer_class = SendSMSSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data['group']
        template_id = serializer.validated_data.get('template_id')
        message = serializer.validated_data.get('message', '')

        if template_id:
            try:
                template = SMSTemplate.objects.get(pk=template_id)
                message = template.template_content
            except SMSTemplate.DoesNotExist:
                return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

        phone_numbers = get_phone_numbers(group)

        if not phone_numbers:
            return Response({'error': 'No phone numbers found'}, status=status.HTTP_400_BAD_REQUEST)

        send_bulk_sms_task.delay(message, phone_numbers, group, template_id)

        return Response({'message': 'SMS sending in progress'}, status=status.HTTP_200_OK)


class SMSSentHistoryListView(generics.ListAPIView):
    queryset = SMSSentHistory.objects.all()
    serializer_class = SMSSentHistorySerializer
    pagination_class = SMSTemplatePagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['group', 'message', 'status']


class SMSStatsView(generics.GenericAPIView):
    serializer_class = SMSStatsSerializer

    def get(self, request, *args, **kwargs):
        today = timezone.now()
        total_sent = SMSSentHistory.objects.count()
        sent_this_month = SMSSentHistory.objects.filter(
            sent_at__month=today.month,
            sent_at__year=today.year,
        ).count()
        success = SMSSentHistory.objects.filter(status='Success').count()
        failed = SMSSentHistory.objects.filter(status='Failed').count()
        pending = SMSSentHistory.objects.filter(status='Pending').count()

        return Response({
            'total_sent': total_sent,
            'sent_this_month': sent_this_month,
            'success': success,
            'failed': failed,
            'pending': pending,
        })


class SMSBalanceView(generics.GenericAPIView):
    serializer_class = SMSStatsSerializer

    def get(self, request, *args, **kwargs):
        result = get_balance()
        return Response(result)


class SMSReportView(generics.GenericAPIView):
    serializer_class = SMSStatsSerializer

    def get(self, request, request_id, *args, **kwargs):
        result = get_report(request_id)
        return Response(result)