# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
# from django.utils import timezone
# from datetime import timedelta

# # তোর অ্যাপের নাম অনুযায়ী মডেল ও সিরিয়ালাইজার ইমপোর্ট করবি
# from .models import Library_Attendance
# from apps.students.models import Student 
# from .serializers import AttendanceSerializer

# class AttendanceListCreate(generics.ListCreateAPIView):
#     serializer_class = AttendanceSerializer
#     parser_classes = [FormParser, MultiPartParser] 

#     def get_queryset(self):
#         # এন্ট্রি টাইমের ভিত্তিতে লেটেস্ট ডাটা আগে দেখাবে
#         queryset = Library_Attendance.objects.all().order_by('-entry_time')
#         filter_type = self.request.query_params.get('filter')
#         today = timezone.now().date()

#         # Figma-র ফিল্টারিং লজিক
#         if filter_type == 'inside':
#             return queryset.filter(exit_time__isnull=True) # বর্তমানে যারা ভেতরে আছে
#         elif filter_type == 'today':
#             return queryset.filter(entry_time__date=today)
#         elif filter_type == 'week':
#             start_of_week = today - timedelta(days=today.weekday())
#             return queryset.filter(entry_time__date__range=[start_of_week, today])
#         elif filter_type == 'month':
#             return queryset.filter(entry_time__year=today.year, entry_time__month=today.month)
            
#         return queryset

#     def create(self, request, *args, **kwargs):
#         # সোয়াইগার/ফ্রন্টএন্ড থেকে আসা আইডি ধরছি
#         sid = request.data.get('Library_student_id') or request.data.get('student')
#         book = request.data.get('book_name', 'Not Specified')

#         if not sid:
#             return Response({"error": "Student ID প্রদান করা হয়নি"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # ডাটাবেজের Primary Key (৩ বা ৫) দিয়ে স্টুডেন্ট প্রোফাইল খোঁজা
#             student_obj = Student.objects.get(id=int(sid))
            
#             # নতুন অ্যাটেনডেন্স রেকর্ড তৈরি
#             attendance = Library_Attendance.objects.create(
#                 student=student_obj, 
#                 book_name=book,
#                 Library_student_id=str(sid) # Figma কলামের জন্য স্টোর করা
#             )
            
#             serializer = self.get_serializer(attendance)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
            
#         except Student.DoesNotExist:
#             return Response({"error": f"ID {sid} এর কোনো স্টুডেন্ট পাওয়া যায়নি!"}, status=status.HTTP_404_NOT_FOUND)
#         except ValueError:
#             return Response({"error": "ID অবশ্যই একটি সংখ্যা হতে হবে"}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class AttendanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Library_Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#     parser_classes = [FormParser, MultiPartParser]

#     def perform_update(self, serializer):
#         # চেক-আউট করার সময় বর্তমান সময় সেট হবে
#         # মনে রাখিস: মডেলে যেন exit_time এ auto_now=True না থাকে
#         serializer.save(exit_time=timezone.now())


