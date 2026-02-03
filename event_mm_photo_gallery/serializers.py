from rest_framework import serializers
from .models import *
import re

class PhotoGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoGallery
        fields = '__all__'
        




class VideoGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoGallery
        fields = '__all__'
    def validate_video_url(self, value):
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        if not re.match(youtube_regex, value):
            raise serializers.ValidationError("অনুগ্রহ করে একটি সঠিক ইউটিউব লিঙ্ক প্রদান করুন।")
        return value