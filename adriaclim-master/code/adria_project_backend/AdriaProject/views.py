import os
import json
from django.conf import settings
from django.shortcuts import render


def welcome_page(request):
    json_path = os.path.join(settings.BASE_DIR, 'static/assets/configuration/welcomePage.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        welcome_data = json.load(f)
    return render(request, "welcome.html", {"welJson": welcome_data})
