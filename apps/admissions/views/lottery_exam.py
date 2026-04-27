from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.admissions.models import StudentAdmission, LotterySession
from apps.admissions.services.lottery_service import assign_sequential_numbers, execute_lottery

class LotteryExamViewSet(ViewSet):
    """
    Endpoints controlling Admission Exam & Lottery mechanics
    """
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        class_name = request.query_params.get('class', 'class 6')
        apps = StudentAdmission.objects.filter(desired_class__name__iexact=class_name)
        
        return Response({
            "total_applications": apps.count(),
            "available_seats": 350, # Replace with dynamic logic based on actual sections
            "selected_students": apps.filter(admission_status='selected').count(),
            "pending_selections": apps.filter(admission_status='pending').count()
        })

    @action(detail=False, methods=['post'])
    def assign_numbers(self, request):
        class_name = request.data.get('class', 'class 6')
        count = assign_sequential_numbers(class_name)
        return Response({"message": f"Successfully assigned Admin Forms to {count} applicants."})

    @action(detail=False, methods=['post'])
    def execute(self, request):
        class_name = request.data.get('class', 'class 6')
        num_seats = int(request.data.get('seats', 100))
        
        winners_count = execute_lottery(class_name, num_seats)
        return Response({
            "message": "Lottery successful!",
            "newly_selected": winners_count
        })
