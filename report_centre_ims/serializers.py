from rest_framework import serializers


class SystemOverviewSerializer(serializers.Serializer):
    active_students = serializers.IntegerField()
    active_staff = serializers.IntegerField()
    total_assets = serializers.IntegerField()
    active_sessions = serializers.IntegerField()


class SystemActivitySerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    user = serializers.CharField()
    action = serializers.CharField()
    module = serializers.CharField()
    ip_address = serializers.CharField()
    status = serializers.CharField()



class UserManagementSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField()
    last_login = serializers.DateTimeField()
    account_status = serializers.CharField()


class InventoryManagementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.CharField()
    item_name = serializers.CharField()
    quantity = serializers.IntegerField()
    total_capacity = serializers.IntegerField()
    status = serializers.CharField()
    notes = serializers.CharField()