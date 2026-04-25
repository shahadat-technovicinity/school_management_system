from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.logistics import ExamAdmitCard, ExamSeatPlan, TeacherDuty
from ..serializers.logistics import (
    ExamAdmitCardSerializer, ExamSeatPlanSerializer, TeacherDutySerializer
)

class ExamAdmitCardViewSet(viewsets.ModelViewSet):
    queryset = ExamAdmitCard.objects.all()
    serializer_class = ExamAdmitCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='generate-bulk')
    def bulk_generate(self, request):
        """
        Custom logic to generate admit cards for a whole class or section
        """
        exam_id = request.data.get('exam_setup')
        class_id = request.data.get('class_id')
        # Here you would query students and create cards
        return Response({"status": "Bulk generation started"}, status=status.HTTP_202_ACCEPTED)

class ExamSeatPlanViewSet(viewsets.ModelViewSet):
    queryset = ExamSeatPlan.objects.all()
    serializer_class = ExamSeatPlanSerializer

    @action(detail=False, methods=['get'])
    def room_visualization(self, request):
        """
        Returns data formatted for the UI grid visualization seen in Figma
        """
        room = request.query_params.get('room')
        # Logic to return seat mapping
        return Response({"room": room, "seats": []})

class TeacherDutyViewSet(viewsets.ModelViewSet):
    queryset = TeacherDuty.objects.all()
    serializer_class = TeacherDutySerializer
