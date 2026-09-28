from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import ExamDuty
from .serializers import ExamDutySerializer, ExamDutyStatusUpdateSerializer


class ExamDutyListCreateView(generics.ListCreateAPIView):
    """
    List exam duties:
    - Admin/Staff see all teacher duties.
    - Logged-in Teacher sees ONLY their own duties.
    - Filter by ?teacher_id=X for specific teacher (Admin only).
    """
    serializer_class = ExamDutySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ExamDuty.objects.select_related('teacher__user').all()

        # ১. অ্যাডমিন / সুপারইউজার হলে সব দেখতে পারবেন
        if user.is_staff or user.is_superuser:
            # অ্যাডমিন চাইলে নির্দিষ্ট কোনো টিচারের ID দিয়েও ফিল্টার করতে পারবে
            teacher_id = self.request.query_params.get('teacher_id')
            if teacher_id and teacher_id.isdigit():
                queryset = queryset.filter(teacher_id=int(teacher_id))
            return queryset

        # ২. সাধারণ টিচার হলে শুধু তার নিজের Profile-এর সাথে ম্যাচ করা ডিউটিগুলো ফিল্টার হবে
        if hasattr(user, 'teacher_staff_profile'):
            return queryset.filter(teacher=user.teacher_staff_profile)

        # ৩. যদি ইউজার টিচারও না হয় এবং অ্যাডমিনও না হয়
        return ExamDuty.objects.none()

    def perform_create(self, serializer):
        # শুধু অ্যাডমিন বা স্টাফ নতুন ডিউটি তৈরি / অ্যাসাইন করতে পারবে
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can assign exam duties.")
        serializer.save()


class TeacherMyExamDutyListView(generics.ListAPIView):
    """
    Dedicated View: লগইন করা টিচারের নিজের ডিউটি দেখার জন্য (Explicit Endpoint)
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
    Retrieve, update or delete a specific teacher duty.
    """
    queryset = ExamDuty.objects.select_related('teacher__user').all()
    serializer_class = ExamDutySerializer


class ExamDutyStatusUpdateView(generics.UpdateAPIView):
    """
    Update status of an exam duty (Pending / Confirmed / Conflict).
    """
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutyStatusUpdateSerializer
