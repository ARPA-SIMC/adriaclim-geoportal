from django import forms
from django.forms.widgets import PasswordInput
from .models import *
class UtenteForm(forms.Form):
    name=forms.CharField(max_length=650,required=True)
    surname=forms.CharField(max_length=800,required=True)
    email=forms.CharField(max_length=320,required=True)
    password=forms.CharField(max_length=32,min_length=6,required=True,widget=PasswordInput())
    role_name=forms.ModelChoiceField(queryset=Ruolo.objects.all(),required=True)
    ente_name=forms.ModelChoiceField(queryset=Ente.objects.all(),required=True)
    

class DeleteUserForm(forms.Form):
    email_delete=forms.CharField(widget=forms.HiddenInput())
  

class UpdateUserForm(forms.Form):
    name=forms.CharField(max_length=650,required=True)
    surname=forms.CharField(max_length=800,required=True)
    email=forms.CharField(max_length=320,required=True)
    password=forms.CharField(max_length=32,min_length=6,required=True,widget=PasswordInput())
    confirm_password=forms.CharField(max_length=32,min_length=6,required=True,widget=PasswordInput())
    role_name=forms.ModelChoiceField(queryset=Ruolo.objects.all(),required=True)
    ente_name=forms.ModelChoiceField(queryset=Ente.objects.all(),required=True)
