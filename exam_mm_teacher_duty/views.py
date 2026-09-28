from rest_framework import generics, permissions
from .models import ExamDuty
from .serializers import ExamDutySerializer, ExamDutyStatusUpdateSerializer


class ExamDutyListCreateView(generics.ListCreateAPIView):
    """
    Public View: Anyone can view all duties or create a new duty (AllowAny).
    """
    queryset = ExamDuty.objects.select_related('teacher__user').all()
    serializer_class = ExamDutySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optional filter: ?teacher_id=1
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id and teacher_id.isdigit():
            queryset = queryset.filter(teacher_id=int(teacher_id))
        return queryset


class TeacherMyExamDutyListView(generics.ListAPIView):
    """
    Authenticated View: Only logged-in teacher can see their OWN duties.
    """
    serializer_class = ExamDutySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'teacher_staff_profile'):
            return ExamDuty.objects.select_related('teacher__user').filter(
                teacher=user.teacher_staff_profile
            )
        return ExamDuty.objects.none()


class ExamDutyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Public View: Retrieve, update or delete specific duty (AllowAny).
    """
    queryset = ExamDuty.objects.select_related('teacher__user').all()
    serializer_class = ExamDutySerializer
    permission_classes = [permissions.AllowAny]


class ExamDutyStatusUpdateView(generics.UpdateAPIView):
    """
    Public View: Update duty status (AllowAny).
    """
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutyStatusUpdateSerializer
    permission_classes = [permissions.AllowAny]