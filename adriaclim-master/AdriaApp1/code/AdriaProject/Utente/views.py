from django.contrib import messages
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .forms import UtenteForm,UpdateUserForm
from django.contrib.auth.hashers import make_password
from .models import *
# Create your views here.
def index(request):
    all_users=Utente.objects.all()
    form_user=UtenteForm()  
    if request.method== "POST":
        if 'user_delete' in request.POST:
           delete_email=request.POST["delete_email"]
           utente_delete=Utente.objects.get(email=delete_email)
           utente_delete.delete()
           return render(request,"administration.html",{'form_user':form_user,'all_users':all_users})
        
        elif 'add_user' in request.POST:
            form_user=UtenteForm(request.POST)
            if form_user.is_valid():
                utente_email=form_user.cleaned_data["email"]
                try:
                    u=Utente.objects.get(email=utente_email)
                    messages.info(request,"A user with this email already exists, update it")
                    return render(request,"administration.html",{'form_user':form_user,'all_users':all_users})
                except Utente.DoesNotExist:
                        utente_name=form_user.cleaned_data["name"]
                        utente_surname=form_user.cleaned_data["surname"]
                        utente_password=form_user.cleaned_data["password"]
                        t_hashed = make_password(utente_password)
                        utente_ruolo_name=form_user.cleaned_data["role_name"]
                        utente_ente_name=form_user.cleaned_data["ente_name"]
                        utente_ente=Ente.objects.get(ente_name=utente_ente_name)
                        utente_role=Ruolo.objects.get(ruolo_name=utente_ruolo_name)
                        utente=Utente(email=utente_email,name=utente_name,surname=utente_surname,hash_pass=t_hashed,ente=utente_ente,
                        ruolo=utente_role)
                        utente.save()
                        return render(request,"administration.html",{'form_user':form_user,'all_users':all_users})
               
        elif 'update_user' in request.POST:
            return redirect("administration/modify")

        elif 'data_passed' in request.POST:
            form_update_user=UpdateUserForm(request.POST)
            form_user=UtenteForm()
            if form_update_user.is_valid():
                    utente_email=form_update_user.cleaned_data["email"]
                    u=Utente.objects.get(email=utente_email)
                    if form_update_user.cleaned_data["password"]!=form_update_user.cleaned_data["confirm_password"]:
                            messages.info(request,"The two passwords you passed are not the same, retry")
                            return render(request,"administration.html", {'form_user':form_user,'all_users':all_users})
                    else:
                            utente_name=form_update_user.cleaned_data["name"]
                            utente_surname=form_update_user.cleaned_data["surname"]
                            utente_pass=form_update_user.cleaned_data["password"]
                            hashes_pass=make_password(utente_pass)
                            utente_ente_name=form_update_user.cleaned_data["ente_name"]
                            utente_ruolo_name=form_update_user.cleaned_data["role_name"]
                            utente_ente=Ente.objects.get(ente_name=utente_ente_name)
                            utente_role=Ruolo.objects.get(ruolo_name=utente_ruolo_name)
                            u.name=utente_name
                            u.surname=utente_surname
                            u.email=utente_email
                            u.hash_pass=hashes_pass
                            u.ruolo=utente_role
                            u.ente=utente_ente
                            u.save()
                            all_users=Utente.objects.all()
                            messages.info(request,"The user is correctly updated!")
                            return render(request,"administration.html", {'form_user':form_user,'all_users':all_users})
                
    else:
        return render(request,"administration.html",{'form_user':form_user,'all_users':all_users})
        
    

def modify(request):
    if request.method=="POST":
        if "data_passed" in request.POST:
          form_update_user=UpdateUserForm(request.POST)
          if form_update_user.is_valid():
                    utente_email=form_update_user.cleaned_data["email"]
                    u=Utente.objects.get(email=utente_email)
                    if form_update_user.cleaned_data["password"]!=form_update_user.cleaned_data["confirm_password"]:
                            messages.info(request,"The two passwords you passed are not the same, retry")
                            return render(request,"modify_user.html", {'form_update_user':form_update_user})
                    else:
                            utente_name=form_update_user.cleaned_data["name"]
                            utente_surname=form_update_user.cleaned_data["surname"]
                            utente_pass=form_update_user.cleaned_data["password"]
                            hashes_pass=make_password(utente_pass)
                            utente_ente_name=form_update_user.cleaned_data["ente_name"]
                            utente_ruolo_name=form_update_user.cleaned_data["role_name"]
                            utente_ente=Ente.objects.get(ente_name=utente_ente_name)
                            utente_role=Ruolo.objects.get(ruolo_name=utente_ruolo_name)
                            u.name=utente_name
                            u.surname=utente_surname
                            u.email=utente_email
                            u.hash_pass=hashes_pass
                            u.ruolo=utente_role
                            u.ente=utente_ente
                            u.save()
                            messages.info(request,"The user is correctly updated!")
                            return render(request,"modify_user.html", {'form_update_user':form_update_user})
        else:
            update_email=request.POST["update_email"]
            user_update=Utente.objects.get(email=update_email)
            form_update_user=UpdateUserForm(initial={"name":user_update.name,
                                        "surname":user_update.surname,"email":user_update.email,"role_name":user_update.ruolo,"ente_name":user_update.ente,
                                        "password":"","confirm_password":""})
            return render(request,"modify_user.html", {'form_update_user':form_update_user})      
                        
    
    return render(request,"modify_user.html", {'form_update_user':form_update_user})

    

        