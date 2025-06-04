from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Profile)
admin.site.register(VerificationCode)  
admin.site.register(Cours)
admin.site.register(Exercice)
admin.site.register(Module)