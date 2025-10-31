from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ExmQuestionBank
from .serializers import QuestionBankSerializer

# --- 1. Teacher Upload (Create) and List View ---
class QuestionListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExmQuestionBank.objects.all().order_by('-date_created') 
    serializer_class = QuestionBankSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Teacher create  'uploaded_by' set  status 'pending' 
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user) 

# --- 2. Retrieve View (Teacher ) ---
class QuestionRetrieveAPIView(generics.RetrieveAPIView):
    # এই ভিউ-এ Update/Delete করার কোনো সুযোগ নেই
    queryset = ExmQuestionBank.objects.all()
    serializer_class = QuestionBankSerializer
    permission_classes = [permissions.IsAuthenticated] 

# --- 3. Admin Status Change (Admin) ---
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def admin_change_status(request, pk):
    q = get_object_or_404(ExmQuestionBank, pk=pk)

    new_status = request.data.get('status')
    
    valid_status_values = [choice[0] for choice in ExmQuestionBank.STATUS_CHOICES] 
    
    if new_status not in valid_status_values:
        return Response(
            {"detail": f"Invalid status. Must be one of {valid_status_values}."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    q.status = new_status
    q.save()
    serializer = QuestionBankSerializer(q)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --- 4. Admin Pending Question List View ---
class AdminPendingQuestionListAPIView(generics.ListAPIView):
    queryset = ExmQuestionBank.objects.filter(status='pending').order_by('-date_created')
    serializer_class = QuestionBankSerializer
    permission_classes = [permissions.IsAdminUser]




