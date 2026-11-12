from rest_framework import serializers

from .models import FeeHead


class FeeHeadSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = FeeHead
        fields = [
            'id', 'name', 'parent', 'parent_name', 'has_children',
            'description', 'order', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        ref_name = 'FeeHead'

    def get_has_children(self, obj):
        return obj.children.exists()

    def validate(self, attrs):
        instance = self.instance
        name = attrs.get('name', getattr(instance, 'name', None))
        parent = attrs['parent'] if 'parent' in attrs else getattr(instance, 'parent', None)

        # একই parent এর নিচে একই নাম দুবার না
        siblings = FeeHead.objects.filter(parent=parent, name__iexact=name)
        if instance:
            siblings = siblings.exclude(pk=instance.pk)
        if siblings.exists():
            raise serializers.ValidationError({'name': "এই স্তরে এই নামে আগে থেকেই fee আছে।"})

        # নিজেকে বা নিজের নিচের কাউকে parent বানানো যাবে না
        if instance and parent:
            node = parent
            while node is not None:
                if node.pk == instance.pk:
                    raise serializers.ValidationError(
                        {'parent': "নিজেকে বা নিজের নিচের কোনো fee কে parent বানানো যাবে না।"}
                    )
                node = node.parent
        return attrs