from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

from .models import QuestionBank
from .serializers import QuestionBankSerializer, QuestionBankStatusUpdateSerializer


class QuestionBankListCreateView(generics.ListCreateAPIView):
    """
    List all questions or upload a new question (Default status: pending).
    """
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(uploaded_by=user, status='pending')


class QuestionBankDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a question bank entry.
    """
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    parser_classes = (MultiPartParser, FormParser)


class QuestionBankStatusUpdateView(generics.UpdateAPIView):
    """
    Admin action: Change question status to 'approved' or 'rejected'.
    """
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankStatusUpdateSerializer

    @swagger_auto_schema(
        operation_summary="Approve or Reject Question",
        operation_description="Update status to 'approved' or 'rejected'.",
        request_body=QuestionBankStatusUpdateSerializer
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)