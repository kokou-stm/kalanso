from django.urls import path
from .views import *

urlpatterns = [
    path('modules/', list_modules, name='list_modules'),
    path('moduleslist/', api_modules, name='api_modules'),
    path('modules/create/', create_module, name='create_module'),
    path('modules/<int:module_id>/delete/', delete_module, name='delete_module'),
    path('modules/<int:module_id>/update/', update_module, name='update_module'),
    path("module-details/<str:code>/", module_details, name="module-details"),
    path("create-content/", create_content, name="create_content"),
    path('get-feedback/<str:code>/', get_feedback, name='get_feedback'),
    path('save-training-data/', save_training_data, name='save_training_data'),
]
