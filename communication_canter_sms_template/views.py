from rest_framework import generics, filters, pagination, parsers
from .models import SMSTemplate
from .serializers import SMSTemplateSerializer

## sms template list/create API with pagination and search
class SMSTemplatePagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class SMSTemplateListCreateView(generics.ListCreateAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    pagination_class = SMSTemplatePagination

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    
    filter_backends = [filters.SearchFilter]
    search_fields = ['template_name', 'category', 'template_content']


## sms template detail/update/delete API
class SMSTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
