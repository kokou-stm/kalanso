from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.utils import timezone
import uuid
import unicodedata
from django.utils.text import slugify
import os
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    job = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    status = models.CharField(max_length=50, default='offline')
    last_seen = models.DateTimeField(default=timezone.now)

    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timezone.timedelta(seconds=30)


class VerificationCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_code')
    code = models.CharField(max_length=6, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = str(uuid.uuid4().int)[:6]
        self.save()



def clean_filename(instance, filename):
    """
    Nettoie le nom du fichier pour éviter les caractères problématiques.
    - Remplace les accents par leurs équivalents non accentués.
    - Transforme en slug.
    """
    name, ext = os.path.splitext(filename)  # Séparer le nom et l'extension
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')  # Supprimer accents
    name = slugify(name)  # Convertir en slug (remplace espaces et caractères spéciaux par des tirets)
    return f"uploads/{name}{ext}"  # Ajouter le chemin et l'extension


# class Cours(models.Model):
#     title = models.CharField(max_length=100)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cours')
#     file = models.FileField(upload_to=clean_filename,  blank=True, null=True)
#     def __str__(self):
#         return self.title



from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('professeur', 'Professeur'),
        ('admin', 'Administrateur'),
        ('facilitateur', 'Facilitateur'),
        ('fournisseur', 'Fournisseur de contenu'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )



class Module(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    domaine = models.CharField(max_length=100, null=True, blank=True)
    niveau = models.CharField(max_length=50, null=True, blank=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name__in': ['professeur', 'fournisseur']})
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-date_creation']

# Cours dans un module
class Cours(models.Model):
    module = models.ForeignKey(Module, related_name='cours', on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cours')
    file = models.FileField(upload_to=clean_filename,  blank=True, null=True)

# Exercice généré par IA
class Exercice(models.Model):
    titre = models.CharField(max_length=255, blank=True, null=True)
    module = models.ForeignKey(Module, related_name='exercices', on_delete=models.CASCADE)
    question = models.TextField()
    reponse_attendue = models.TextField()
    source_rag = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

# Quiz généré par IA
class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizz', on_delete=models.CASCADE)
    question = models.TextField()
    choix = models.JSONField()  # Ex: {"a": "...", "b": "...", "c": "...", "d": "..."}
    bonne_reponse = models.CharField(max_length=1)
    source_rag = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

# Évaluation (plus globale, type examen ou test de fin)
class Evaluation(models.Model):
    module = models.ForeignKey(Module, related_name='evaluations', on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    consignes = models.TextField()
    contenu = models.JSONField()  # Contient plusieurs questions ou tâches
    source_rag = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

# Participation des étudiants aux évaluations
class ResultatEvaluation(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'etudiant'})
    soumission = models.JSONField()
    note = models.FloatField(null=True, blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.description

