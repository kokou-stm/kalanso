from django.urls import path, include
from .views import *

urlpatterns = [
    path('/home', home, name='home'),
    path("", index, name="index"),
    
    path('register/', register, name='register'),
    path('login/', connection, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path("dash_board/",user_dashboard, name='user_dashboard'),
    path('upload/', upload_cours, name='upload_cours'),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('updatepassword/<str:token>/<str:uid>/', updatepassword, name='updatepassword'),  
    path('api/modules/', list_modules, name='list_modules'),
    path('api/modules/create/', create_module, name='create_module'),
    path('api/modules/<int:module_id>/delete/', delete_module, name='delete_module'),
    path('api/modules/<int:module_id>/update/', update_module, name='update_module'),
     path("api/module-details/<str:code>/", module_details, name="module-details"),
     path("api/create-content/", create_content, name="create_content"),
      path('api/get-feedback/<str:code>/', get_feedback, name='get_feedback'),
 
]   