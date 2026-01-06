# committees/views.py
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


from .models import *
from .serializers import *

class CommitteeMemberViewCreate(generics.ListCreateAPIView):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer


class CommitteeMemberDelUp(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer



class CommitteeDashboardView(APIView):
    """Dashboard data - count and term end year"""
    
    def get(self, request):
        committees = ['PTA', 'MMC', 'CABINET']
        result = []
        
        for committee_type in committees:
            # Count members
            members = CommitteeMember.objects.filter(
                committee_type=committee_type, 
                is_active=True
            )
            count = members.count()
            
            # Get term info from first member
            first_member = members.first()
            
            if first_member and first_member.term_end:
                term_end_year = first_member.term_end.year
                
                # Calculate term duration properly
                term_duration = (first_member.term_end - first_member.term_start).days // 365
                
                result.append({
                    'committee_type': committee_type,
                    'total_members': count,
                    'term_end': term_end_year,
                    'term_duration_years': term_duration
                })
            else:
                result.append({
                    'committee_type': committee_type,
                    'total_members': count,
                    'term_end': None,
                    'term_duration_years': 0
                })
        
        return Response(result)




# ১০ জনের জন্য কাস্টম প্যাজিনেশন ক্লাস
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommitteeMemberListView(generics.ListAPIView):
    serializer_class = CommitteeMemberSerializer
    pagination_class = StandardResultsSetPagination
    
    ##Filter by commitee type wise commitee
    def get_queryset(self):
        committee_type = self.request.query_params.get('type')
        if committee_type:
            queryset = CommitteeMember.objects.filter(committee_type=committee_type).order_by('-id')
        else:
            queryset = CommitteeMember.objects.all().order_by('-id')
        return queryset