# institution/serializers.py
from rest_framework import serializers
from .models import *

#instituteinfobasicserializer
class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'


#instituteinfodetailsseralizer
class InstitutionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionDetails
        fields = '__all__'



#instituteinfobankserializer
class InstituteBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteInfoBank
        fields = '__all__'


#instituteinfobankserializer
class InstituteOthersSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituteOthers
        fields = '__all__'