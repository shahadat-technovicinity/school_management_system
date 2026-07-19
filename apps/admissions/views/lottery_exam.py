from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.admissions.models import StudentAdmission, LotterySession
from apps.admissions.serializers.lottery_serializers import (
    LotteryStatsSerializer,
    AssignNumbersSerializer,
    ExecuteLotterySerializer,
)
from apps.admissions.services.lottery_service import (
    assign_sequential_numbers,
    execute_lottery,
)


class LotteryExamViewSet(ViewSet):
    """
    Endpoints controlling Admission Exam & Lottery mechanics
    """

    def _get_available_seats(self, class_name):
        """
        Dynamically resolves available seats from the latest LotterySession
        configured for the given class. Falls back to 0 if none configured.
        """
        session = (
            LotterySession.objects
            .filter(target_class__iexact=class_name)
            .order_by('-created_at')
            .first()
        )
        return session.total_seats if session else 0

    @action(detail=False, methods=['get'])
    def stats(self, request):
        serializer = LotteryStatsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        class_name = serializer.validated_data['class_name']

        apps = StudentAdmission.objects.filter(desired_class__iexact=class_name)
        available_seats = self._get_available_seats(class_name)
        selected = apps.filter(admission_status='selected').count()

        return Response({
            "class_name": class_name,
            "total_applications": apps.count(),
            "available_seats": available_seats,
            "remaining_seats": max(available_seats - selected, 0),
            "selected_students": selected,
            "pending_selections": apps.filter(admission_status='pending').count(),
        })

    @action(detail=False, methods=['post'])
    def assign_numbers(self, request):
        serializer = AssignNumbersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        class_name = serializer.validated_data['class_name']

        count = assign_sequential_numbers(class_name)
        return Response({
            "message": f"Successfully assigned Admin Forms to {count} applicants.",
            "class_name": class_name,
            "assigned_count": count,
        })

    @action(detail=False, methods=['post'])
    def execute(self, request):
        serializer = ExecuteLotterySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        class_name = serializer.validated_data['class_name']

        # Dynamic seats: use payload if provided, else the configured session seats
        num_seats = serializer.validated_data.get('seats')
        if num_seats is None:
            num_seats = self._get_available_seats(class_name)

        if num_seats <= 0:
            return Response(
                {"error": f"No seats configured for '{class_name}'. "
                          f"Create a LotterySession or pass 'seats' in the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        winners_count = execute_lottery(class_name, num_seats)
        return Response({
            "message": "Lottery successful!",
            "class_name": class_name,
            "seats_used": num_seats,
            "newly_selected": winners_count,
        })