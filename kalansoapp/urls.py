from django.urls import path
from .views import *

urlpatterns = [
    path('home', home, name='home'),
    path("", index, name="index"),
    path('register/', register, name='register'),
    path('login/', connection, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path("dash_board/", user_dashboard, name='user_dashboard'),
    path('upload/', upload_cours, name='upload_cours'),
    path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('updatepassword/<str:token>/<str:uid>/', updatepassword, name='updatepassword'),
]
