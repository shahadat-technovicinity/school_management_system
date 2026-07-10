from rest_framework import serializers
from .models import Role, Feature, RolePermission


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name', 'display_name']


class RolePermissionSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(read_only=True)
    feature_id = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(),
        source='feature',
        write_only=True
    )

    class Meta:
        model = RolePermission
        fields = [
            'id', 'feature', 'feature_id',
            'can_view', 'can_create', 'can_edit', 'can_delete'
        ]


# Role এর সব Feature permission একসাথে দেখানোর জন্য
class RoleFeaturePermissionSerializer(serializers.Serializer):
    feature_id = serializers.IntegerField()
    feature_name = serializers.CharField()
    display_name = serializers.CharField()
    can_view = serializers.BooleanField()
    can_create = serializers.BooleanField()
    can_edit = serializers.BooleanField()
    can_delete = serializers.BooleanField()


# Bulk update এর জন্য
class BulkPermissionSerializer(serializers.Serializer):
    feature_id = serializers.PrimaryKeyRelatedField(queryset=Feature.objects.all())
    can_view = serializers.BooleanField(default=False)
    can_create = serializers.BooleanField(default=False)
    can_edit = serializers.BooleanField(default=False)
    can_delete = serializers.BooleanField(default=False)


class RoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'created_at', 'permissions']