from django.forms import forms
from django.forms.widgets import ClearableFileInput
from .models import account_info

class Profilepic(forms.Form):
    profilepic = forms.FileField()
    
class file_form(forms.Form):
    required_files = forms.FileField(widget=ClearableFileInput(attrs={'multiple':True}))

class new_account_form(forms.Form):

    class Meta:
        model = account_info
        fields = ('meternumber','initial_meter_reading','rateid','barangay')
    

