from django.http.response import HttpResponse, JsonResponse
from Dataset.forms import DatasetForm
from django.shortcuts import render
from myFunctions import allFunctions


# Create your views here.
def getMetadataForm(request,dataset_id):
    if request.method=="GET":
        form=DatasetForm(request.GET)
        if form.is_valid():
            id_passed=form.cleaned_data['dataset_id']
            allFunctions.getMetadataOfASpecificDataset(id_passed)
            return render(request,"specificDataset.html")

    allFunctions.getMetadataOfASpecificDataset(dataset_id)
    return render(request,"specificDataset.html")

