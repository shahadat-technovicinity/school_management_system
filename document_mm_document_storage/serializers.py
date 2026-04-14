from django.db import transaction
from rest_framework import serializers
from .models import Cabinet, Shelf, Document, LocationMoveLog


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Shelf
        fields = ['id', 'name', 'cabinet']


class CabinetSerializer(serializers.ModelSerializer):
    shelves = ShelfSerializer(many=True, read_only=True)

    class Meta:
        model  = Cabinet
        fields = ['id', 'name', 'location', 'shelves']


class LocationMoveLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LocationMoveLog
        fields = [
            'id', 'from_cabinet', 'from_shelf',
            'to_cabinet', 'to_shelf',
            'reason_for_move', 'notes', 'moved_at',
        ]
        read_only_fields = ['id', 'moved_at']


class DocumentListSerializer(serializers.ModelSerializer):
    """
    List view এ ব্যবহার হয় — cabinet/shelf নাম সরাসরি দেখায়।
    """
    cabinet_name = serializers.CharField(source='cabinet.name', read_only=True)
    shelf_name   = serializers.CharField(source='shelf.name',   read_only=True)

    class Meta:
        model  = Document
        fields = [
            'id', 'name', 'document_type',
            'cabinet', 'cabinet_name',
            'shelf',   'shelf_name',
            'tag_number', 'status',
            'last_modified_by', 'created_at', 'updated_at',
        ]


class DocumentCreateSerializer(serializers.ModelSerializer):
    """
    Figma Screen 2 — 'Add New Storage' modal.
    একটাই POST-এ document + location সব save হয়।
    User কে আলাদা করে location update করতে হবে না।
    """
    class Meta:
        model  = Document
        fields = [
            'id', 'name', 'document_type',
            'cabinet', 'shelf', 'tag_number',
            'status', 'last_modified_by',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        # Shelf টা selected cabinet-এর অধীনে আছে কিনা check করো
        cabinet = data.get('cabinet')
        shelf   = data.get('shelf')
        if shelf and cabinet and shelf.cabinet != cabinet:
            raise serializers.ValidationError(
                {'shelf': 'এই shelf টা selected cabinet-এর অধীনে নেই।'}
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        document = Document.objects.create(**validated_data)

        # প্রথমবার তৈরিতেও move log রাখো — history পরে কাজে লাগবে
        if document.cabinet or document.shelf:
            LocationMoveLog.objects.create(
                document       = document,
                from_cabinet   = '',
                from_shelf     = '',
                to_cabinet     = document.cabinet.name if document.cabinet else '',
                to_shelf       = document.shelf.name   if document.shelf   else '',
                reason_for_move= 'Initial storage',
                notes          = '',
            )

        return document


class DocumentUpdateLocationSerializer(serializers.Serializer):
    """
    Figma Screen 3 — 'Update Document Location' modal।
    Cabinet, shelf, tag, reason, notes — সব এখানে।
    """
    cabinet         = serializers.PrimaryKeyRelatedField(queryset=Cabinet.objects.all())
    shelf           = serializers.PrimaryKeyRelatedField(queryset=Shelf.objects.all())
    tag_number      = serializers.CharField(max_length=50, required=False, allow_blank=True)
    reason_for_move = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes           = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        shelf   = data.get('shelf')
        cabinet = data.get('cabinet')
        if shelf and cabinet and shelf.cabinet != cabinet:
            raise serializers.ValidationError(
                {'shelf': 'এই shelf টা selected cabinet-এর অধীনে নেই।'}
            )
        return data

    @transaction.atomic
    def update(self, document, validated_data):
        # পুরোনো location save করো log-এর জন্য
        old_cabinet = document.cabinet.name if document.cabinet else ''
        old_shelf   = document.shelf.name   if document.shelf   else ''

        # Document update করো
        document.cabinet    = validated_data['cabinet']
        document.shelf      = validated_data['shelf']
        document.tag_number = validated_data.get('tag_number', document.tag_number)
        document.save()

        # Move log তৈরি করো
        LocationMoveLog.objects.create(
            document        = document,
            from_cabinet    = old_cabinet,
            from_shelf      = old_shelf,
            to_cabinet      = document.cabinet.name,
            to_shelf        = document.shelf.name,
            reason_for_move = validated_data.get('reason_for_move', ''),
            notes           = validated_data.get('notes', ''),
        )

        return document