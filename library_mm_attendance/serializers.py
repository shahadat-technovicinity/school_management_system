from rest_framework import serializers
from apps.students.models import Student
from .models import LibraryAttendance


class LibraryAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    student_class = serializers.SerializerMethodField(read_only=True)
    student_roll = serializers.SerializerMethodField(read_only=True)
    book_name = serializers.SerializerMethodField(read_only=True)
    is_checked_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = LibraryAttendance
        fields = '__all__'
        extra_kwargs = {
            'check_out_time': {'required': False},
            'book': {'required': False},
        }

    def get_student_name(self, obj):
        return obj.student.full_name

    def get_student_class(self, obj):
        return obj.student.class_name_static

    def get_student_roll(self, obj):
        return obj.student.roll_number

    def get_book_name(self, obj):
        return obj.book.book_name if obj.book else None


class QuickEntrySerializer(serializers.Serializer):
    roll_number = serializers.CharField()
    book_id = serializers.IntegerField(required=False)