# from rest_framework import serializers
# from .models import Library_Attendance

# class AttendanceSerializer(serializers.ModelSerializer):
#     # StudentPersonalInfo থেকে নির্দিষ্ট ডাটা টেনে আনা
#     student_name = serializers.ReadOnlyField(source='student.first_name') # অথবা full_name থাকলে সেটা
#     roll = serializers.ReadOnlyField(source='student.roll_number')
#     class_name = serializers.ReadOnlyField(source='student.class_name')
#     section = serializers.ReadOnlyField(source='student.section')

#     class Meta:
#         model = Library_Attendance
#         # এখানে তুই যা যা দেখাবে তা লিখবি
#         fields = [
#             'id', 
#             'Library_student_id', 
#             'student_name', 
#             'roll', 
#             'class_name', 
#             'section', 
#             'book_name', 
#             'entry_time', 
#             'exit_time'
#         ]

         
