"""
URL configuration for lms_project project.

For more information:
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# URL sans préfixe de langue, comme le chemin pour changer la langue
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# URLs traduites avec préfixes /fr/, /en/, /de/, etc.
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('kalansoapp.urls')),  # Remplace 'kalansoapp' si ton app a un nom différent
   # prefix_default_language=False,  # Pour ne pas afficher /fr/ si fr est la langue par défaut
)

# Gestion des fichiers média
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
