from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from academic_class_routine.models import StudentPersonalInfo
from .models import GeneratedIDCard, IDCardTemplate
from .serializers import StudentIDCardSerializer, GenerateCardRequestSerializer
from .services import generate_card_image_service # We will write this next
from .tasks import batch_generate_cards_task # Celery task

class StudentIDCardViewSet(viewsets.ModelViewSet):
    """
    Handles the Dashboard List and Single Generation
    """
    queryset = StudentPersonalInfo.objects.all()
    serializer_class = StudentIDCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter based on UI Dropdowns: Class, Section, Year
        """
        qs = super().get_queryset()
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        academic_year = self.request.query_params.get('academic_year')

        if class_name:
            qs = qs.filter(class_name=class_name)
        if section:
            qs = qs.filter(section=section)
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
            
        return qs

    @action(detail=True, methods=['post'])
    def generate_single(self, request, pk=None):
        """
        API for the "Generate New ID Card" Modal (Right side of UI)
        """
        student = self.get_object()
        template_id = request.data.get('template_id', 1)
        
        try:
            # 1. Generate the Image (Heavy Logic)
            image_file = generate_card_image_service(student, template_id)
            
            # 2. Save to DB
            GeneratedIDCard.objects.create(
                student=student,
                template_id=template_id,
                card_image=image_file,
                generated_by=request.user,
                snapshot_data=StudentIDCardSerializer(student).data
            )
            
            return Response({'message': 'ID Card Generated Successfully', 'status': 'success'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def batch_generate(self, request):
        """
        API for the "Batch ID Card Generation" Screen
        """
        serializer = GenerateCardRequestSerializer(data=request.data)
        if serializer.is_valid():
            student_ids = serializer.validated_data['student_ids']
            template_id = serializer.validated_data['template_id']
            
            # Trigger Celery Task (Non-blocking)
            task = batch_generate_cards_task.delay(student_ids, template_id, request.user.id)
            
            return Response({
                'message': 'Batch generation started in background',
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


from celery.result import AsyncResult
from rest_framework.decorators import api_view

@api_view(['GET'])
def task_status(request, task_id):
    """
    API to check the status of a Celery task.
    """
    task_result = AsyncResult(task_id)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.status,
        'progress': 0
    }
    
    if task_result.status == 'PROGRESS':
        response_data['progress'] = task_result.info.get('current', 0)
        response_data['total'] = task_result.info.get('total', 0)
    elif task_result.status == 'SUCCESS':
        response_data['result'] = task_result.result
    elif task_result.status == 'FAILED':
        response_data['error'] = str(task_result.result)
    
    return Response(response_data)