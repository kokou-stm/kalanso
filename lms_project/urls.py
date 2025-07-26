from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Routes non traduites (ex: APIs et changement de langue)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('kalansoapp.api_urls')),  # ← API hors i18n
]

# Routes traduites avec préfixe /fr/, /en/, etc.
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('kalansoapp.urls')),  # Pages avec interface traduisible
)

# Médias
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
