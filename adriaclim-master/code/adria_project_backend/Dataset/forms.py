from django import forms

class DatasetForm(forms.Form):
    dataset_id=forms.CharField(label="dataset_id")