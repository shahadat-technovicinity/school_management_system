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
        fields = '__all__' # মডেল থেকে ফিল্ড ডিলিট হওয়ায় এটি এখন শুধু টাইটেল আর ইউআরএল নেবে।
        
    def validate_video_url(self, value):
        # প্রতিটা লাইনের আগে 'r' যুক্ত করে স্ট্রিংগুলোকে সেফ করা হয়েছে
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        if not re.match(youtube_regex, value):
            raise serializers.ValidationError("অনুগ্রহ করে একটি সঠিক ইউটিউব লিঙ্ক প্রদান করুন।")
        return value