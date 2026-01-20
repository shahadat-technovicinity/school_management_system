from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ExmQuestionBank
from .serializers import QuestionBankSerializer
from rest_framework.permissions import AllowAny 

# --- 1. List & Create ---
class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExmQuestionBank.objects.all().order_by('-date_created')
    serializer_class = QuestionBankSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
             serializer.save(uploaded_by=self.request.user)
        else:
             serializer.save()


# --- 2. Retrieve ---
class QuestionRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ExmQuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    permission_classes = [AllowAny]


# --- 3. Admin Status Change (POST) ---
@api_view(['POST'])
def admin_change_status(request, pk):
    question = get_object_or_404(ExmQuestionBank, pk=pk)
    new_status = request.data.get('status')
    valid_status_values = [choice[0] for choice in ExmQuestionBank.STATUS_CHOICES]

    if new_status not in valid_status_values:
        return Response(
            {"detail": f"Invalid status. Must be one of {valid_status_values}."},
            status=status.HTTP_400_BAD_REQUEST
        )

    question.status = new_status
    question.save()
    serializer = QuestionBankSerializer(question)
    return Response(serializer.data, status=status.HTTP_200_OK)


# --- 4. Pending Questions List ---
class AdminPendingQuestionListAPIView(generics.ListAPIView):
    serializer_class = QuestionBankSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExmQuestionBank.objects.filter(status='pending').order_by('-date_created')