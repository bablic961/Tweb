from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Кастомный выход
    path('profile/', views.profile_view, name='profile'),
    path('set-nickname/<int:user_id>/', views.set_nickname, name='set_nickname'),
]