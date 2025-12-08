from rest_framework import serializers
from .models import *

class CreateFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateFee
        fields = "__all__"


# fee_management/serializers.py (Continued)

# fee_management/serializers.py (Modified)


# --- ১. FormFillupSubAmount-এর সিরিয়ালাইজার (Sub-Serializer) ---
# ... (এই অংশটি একই থাকবে) ...
# class FormFillupSubAmountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FormFillupSubAmount
#         fields = ['name', 'amount'] 


# # --- ২. CreateFee-এর নেস্টেড সিরিয়ালাইজার (মূল সিরিয়ালাইজার) ---
# class CreateFeeSerializer(serializers.ModelSerializer):
#     # required=False সেট করা হয়েছে, যাতে এটি ঐচ্ছিক হয়
#     sub_amounts = FormFillupSubAmountSerializer(many=True, required=False) 

#     class Meta:
#         model = CreateFee
#         fields = [
#             'id', 'assignment_type', 'select_class', 'select_section', 
#             'fee_type', 'amount', 'due_date', 'payment_period', 
#             'created_at', 'sub_amounts'
#         ]
        
#     # --- ৩. কাস্টম create মেথড (সাব-অ্যামাউন্ট ঐচ্ছিক করার জন্য) ---
    
#     def create(self, validated_data):
#         # validated_data থেকে 'sub_amounts' ডেটা আলাদা করে নিন।
#         # যদি sub_amounts না থাকে, তবে ডিফল্ট হিসাবে একটি খালি তালিকা ([]) ব্যবহার করুন।
#         sub_amounts_data = validated_data.pop('sub_amounts', [])
        
#         # প্রথমে মূল CreateFee অবজেক্ট তৈরি করুন (sub_amounts ডেটা বাদ দিয়েই)
#         create_fee_instance = CreateFee.objects.create(**validated_data)
        
#         # --- কন্ডিশনাল লজিক ---
#         # শুধুমাত্র যদি sub_amounts ডেটা থাকে এবং fee_type হয় 'form_fillup fee' তবেই সেভ হবে
#         if sub_amounts_data and create_fee_instance.fee_type == 'form_fillup fee':
             
#             for sub_amount_item in sub_amounts_data:
#                 # FormFillupSubAmount অবজেক্ট তৈরি করুন
#                 FormFillupSubAmount.objects.create(
#                     fee_assignment=create_fee_instance, 
#                     **sub_amount_item
#                 )
            
#         return create_fee_instance