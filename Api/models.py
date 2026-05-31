from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Register(AbstractUser):
    class Meta:
        verbose_name = "Register"          
        verbose_name_plural = "Register"
    ROLE_CHOICES=(
        ('admin','Admin'),
        ('user',"User"),
    )
    Role=models.CharField(choices=ROLE_CHOICES,default='user')
    def __str__(self):
        return self.username
    

class Resume(models.Model):
    file=models.FileField(upload_to='resume/')
    uploaded_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


# Create your models here.
