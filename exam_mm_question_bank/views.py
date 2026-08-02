from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from .models import ExmQuestionBank
from .serializers import (
    UserQuestionBankSerializer, 
    AdminQuestionBankSerializer, 
    QuestionStatusUpdateSerializer
)


# --- 1. Main Questions List & Create (STRICTLY PENDING) ---
# GET: এখানে শুধুমাত্র 'pending' ডাটা আসবে। নতুন ক্রিয়েট হওয়া প্রশ্ন এখানেই জমা হবে।
# POST: নতুন প্রশ্ন সাবমিট করলে অটোমেটিক status='pending' হবে।
class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = UserQuestionBankSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # শুধু পেন্ডিং ডাটা আসবে। approved বা rejected হয়ে গেলে এখান থেকে সরে যাবে।
        return ExmQuestionBank.objects.filter(status='pending').order_by('-date_created')

    def perform_create(self, serializer):
        user = self.request.user if (hasattr(self.request, 'user') and self.request.user.is_authenticated) else None
        serializer.save(uploaded_by=user, status='pending')


# --- 2. Detail API: Retrieve, Update & Delete ---
class QuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExmQuestionBank.objects.all()
    serializer_class = UserQuestionBankSerializer
    permission_classes = [AllowAny]


# --- 3. Admin: Strictly Approved Questions List ---
class AdminApprovedQuestionListAPIView(generics.ListAPIView):
    serializer_class = AdminQuestionBankSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExmQuestionBank.objects.filter(status='approved').order_by('-date_created')


# --- 4. Admin: Strictly Rejected Questions List ---
class AdminRejectedQuestionListAPIView(generics.ListAPIView):
    serializer_class = AdminQuestionBankSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExmQuestionBank.objects.filter(status='rejected').order_by('-date_created')


# --- 5. Admin: Status Change Only (PATCH ONLY) ---
class AdminQuestionStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = ExmQuestionBank.objects.all()
    serializer_class = QuestionStatusUpdateSerializer
    permission_classes = [AllowAny]
    
    http_method_names = ['patch']

    def perform_update(self, serializer):
        new_status = self.request.data.get('status')
        valid_status_values = [choice[0] for choice in ExmQuestionBank.STATUS_CHOICES]

        if not new_status or new_status not in valid_status_values:
            raise ValidationError(
                {"detail": f"Invalid status. Must be one of {valid_status_values}."}
            )

        serializer.save(status=new_status)