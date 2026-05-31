from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Register
from .models import Resume

admin.site.register(Resume)
admin.site.register(Register,UserAdmin)

# Register your models here.
