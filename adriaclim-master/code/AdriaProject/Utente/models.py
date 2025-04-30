from django.db import models 
# Create your models here.
class Ente(models.Model):
    ente_id=models.CharField(max_length=650,primary_key=True)
    ente_name=models.CharField(max_length=1500,null=False)

    def __str__(self):
       return self.ente_name
    
    class Meta:
        verbose_name_plural="Enti"
    


class Ruolo(models.Model):
    ruolo_id=models.CharField(max_length=650,primary_key=True)
    ruolo_name=models.CharField(max_length=1500,null=False)

    def __str__(self):
        return self.ruolo_name

    class Meta:
        verbose_name_plural="Ruoli"
    


class Utente(models.Model):
    email=models.CharField(max_length=1000,null=False,unique=True)
    name=models.CharField(max_length=1000,null=False)
    surname=models.CharField(max_length=1000,null=False)
    hash_pass=models.CharField(max_length=1650,null=False)
    ente=models.ForeignKey(Ente,on_delete=models.CASCADE,related_name="ente")  #se viene eliminato l'ente si eliminano in cascata tutti i suoi utenti
    ruolo=models.ForeignKey(Ruolo,on_delete=models.CASCADE,related_name="ruolo")

    class Meta:
        # otherwise we get "Utentes in admin"
        verbose_name_plural = "Utenti"
