from Dataset import views
from .views import welcome_page
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dataset/', include('Dataset.urls')),
    path('metadata/', include('Metadata.urls')),
    path('utente/', include('Utente.urls')),
    path('myFunctions/', include('myFunctions.urls')),
    path("", welcome_page, name="welcome"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



