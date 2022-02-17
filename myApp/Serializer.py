from django import forms
from rest_framework import serializers
from django.forms import ClearableFileInput
from .models import *

class consumersInfo_Serializer(serializers.Serializer):
    class Meta:
        model= consumers_info
        fields= '__all__'

class account_info_Serializer(serializers.Serializer):
    class Meta:
        model = account_info
        fields = '__all__'    

class usage_record_Serializer(serializers.Serializer):
    class Meta:
        model = usage_record
        fields = '__all__'   

class Profilepic(forms.Form):
    class Meta:
        model = consumers_info
        fields = ['profilepic',]
        widgets = {
            'profilepic': ClearableFileInput(attrs={'multiple':True}),
        }        