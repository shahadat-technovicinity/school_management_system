from rest_framework import serializers
from django.utils import timezone
from .models import LeaveType, LeaveBalance, TeacherLeave
from teacher.models import Teacher


# ─────────────────────────────────────────────────────────────────────────────
# Leave Type Serializers
# ─────────────────────────────────────────────────────────────────────────────

class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializer for Leave Type - used for listing and details."""
    
    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "description",
            "default_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LeaveTypeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Leave Type."""
    
    class Meta:
        model = LeaveType
        fields = ["name", "description", "default_days", "is_active"]


# ─────────────────────────────────────────────────────────────────────────────
# Leave Balance Serializers
# ─────────────────────────────────────────────────────────────────────────────

class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializer for Leave Balance - shows leave allocation and usage."""
    
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    available = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "teacher",
            "leave_type",
            "leave_type_name",
            "total_allocated",
            "used",
            "available",
            "year",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "available", "created_at", "updated_at"]


class LeaveBalanceSummarySerializer(serializers.Serializer):
    """
    Summary serializer for teacher's leave balance.
    Used in teacher detail page to show leave summary cards.
    """
    leave_type_id = serializers.IntegerField()
    leave_type_name = serializers.CharField()
    total_allocated = serializers.IntegerField()
    used = serializers.IntegerField()
    available = serializers.IntegerField()


# ─────────────────────────────────────────────────────────────────────────────
# Teacher Leave Serializers
# ─────────────────────────────────────────────────────────────────────────────

class TeacherMinimalSerializer(serializers.ModelSerializer):
    """Minimal teacher info for leave list."""
    name = serializers.CharField(source="full_name", read_only=True)
    
    class Meta:
        model = Teacher
        fields = ["id", "teacher_id", "name", "photo"]


class TeacherLeaveListSerializer(serializers.ModelSerializer):
    """Serializer for listing teacher leaves."""
    
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    teacher_id_display = serializers.CharField(source="teacher.teacher_id", read_only=True)
    leave_date_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherLeave
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "teacher_id_display",
            "leave_type",
            "leave_type_name",
            "leave_date",
            "leave_date_display",
            "from_date",
            "to_date",
            "leave_days",
            "no_of_days",
            "status",
            "applied_on",
        ]
        ref_name = "TeacherLeaveList"

    def get_leave_date_display(self, obj):
        """Format leave date range for display."""
        if obj.from_date == obj.to_date:
            return obj.from_date.strftime("%d %b %Y")
        return f"{obj.from_date.strftime('%d %b %Y')} - {obj.to_date.strftime('%d %b %Y')}"


class TeacherLeaveDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single leave application."""
    
    teacher = TeacherMinimalSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.name", read_only=True)
    
    class Meta:
        model = TeacherLeave
        fields = [
            "id",
            "teacher",
            "leave_type",
            "leave_date",
            "from_date",
            "to_date",
            "leave_days",
            "no_of_days",
            "reason",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "admin_remarks",
            "applied_on",
            "created_at",
            "updated_at",
        ]
        ref_name = "TeacherLeaveDetail"


class TeacherLeaveCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a leave application.
    Used by admin to create leave on behalf of teacher.
    """
    
    class Meta:
        model = TeacherLeave
        fields = [
            "teacher",
            "leave_type",
            "leave_date",
            "from_date",
            "to_date",
            "leave_days",
            "no_of_days",
            "reason",
        ]
        ref_name = "TeacherLeaveCreate"

    def validate(self, data):
        """Validate leave application data."""
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        
        if from_date and to_date:
            if to_date < from_date:
                raise serializers.ValidationError({
                    "to_date": "End date cannot be before start date."
                })
        
        # Check for overlapping leaves
        teacher = data.get("teacher")
        if teacher and from_date and to_date:
            overlapping = TeacherLeave.objects.filter(
                teacher=teacher,
                status__in=["pending", "approved"],
                from_date__lte=to_date,
                to_date__gte=from_date
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError(
                    "This leave overlaps with an existing leave application."
                )
        
        return data

    def create(self, validated_data):
        """Create leave application with auto-calculated days."""
        # Calculate no_of_days if not provided
        if not validated_data.get("no_of_days"):
            from_date = validated_data["from_date"]
            to_date = validated_data["to_date"]
            delta = (to_date - from_date).days + 1
            leave_days = validated_data.get("leave_days", "full_day")
            if leave_days in ["first_half", "second_half"]:
                validated_data["no_of_days"] = delta * 0.5
            else:
                validated_data["no_of_days"] = delta
        
        return super().create(validated_data)


class TeacherLeaveUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating leave application (before approval)."""
    
    class Meta:
        model = TeacherLeave
        fields = [
            "leave_type",
            "leave_date",
            "from_date",
            "to_date",
            "leave_days",
            "no_of_days",
            "reason",
        ]
        ref_name = "TeacherLeaveUpdate"

    def validate(self, data):
        """Validate that leave can be updated."""
        instance = self.instance
        if instance and instance.status not in ["pending"]:
            raise serializers.ValidationError(
                "Cannot update leave application that has been approved or declined."
            )
        
        from_date = data.get("from_date", instance.from_date if instance else None)
        to_date = data.get("to_date", instance.to_date if instance else None)
        
        if from_date and to_date and to_date < from_date:
            raise serializers.ValidationError({
                "to_date": "End date cannot be before start date."
            })
        
        return data


class LeaveApprovalSerializer(serializers.Serializer):
    """Serializer for approving/declining leave application."""
    
    action = serializers.ChoiceField(
        choices=["approve", "decline"],
        help_text="Action to perform on the leave application"
    )
    admin_remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional remarks by admin"
    )

    def validate(self, data):
        """Validate that the leave can be approved/declined."""
        leave = self.context.get("leave")
        if leave and leave.status != "pending":
            raise serializers.ValidationError(
                f"Cannot {data['action']} a leave that is already {leave.status}."
            )
        return data

    def save(self, leave, user):
        """Process the approval/decline action."""
        action = self.validated_data["action"]
        admin_remarks = self.validated_data.get("admin_remarks", "")
        
        leave.status = "approved" if action == "approve" else "declined"
        leave.reviewed_by = user
        leave.reviewed_at = timezone.now()
        leave.admin_remarks = admin_remarks
        leave.save()
        
        # Update leave balance if approved
        if action == "approve":
            self._update_leave_balance(leave)
        
        return leave

    def _update_leave_balance(self, leave):
        """Update teacher's leave balance when leave is approved."""
        year = leave.from_date.year
        balance, created = LeaveBalance.objects.get_or_create(
            teacher=leave.teacher,
            leave_type=leave.leave_type,
            year=year,
            defaults={"total_allocated": leave.leave_type.default_days}
        )
        balance.used += int(leave.no_of_days)
        balance.save()


# ─────────────────────────────────────────────────────────────────────────────
# Teacher Leave Summary for Detail Page
# ─────────────────────────────────────────────────────────────────────────────

class TeacherLeaveSummarySerializer(serializers.Serializer):
    """
    Complete leave summary for teacher detail page.
    Includes balance cards and leave history.
    """
    leave_balances = LeaveBalanceSummarySerializer(many=True)
    recent_leaves = TeacherLeaveListSerializer(many=True)
    total_leaves_taken = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
