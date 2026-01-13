# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # Card marker management (admin-only)
    path('cardmarkers/create/', views.admin_create_cardmarker, name='create_cardmarker'),
    path('cardmarkers/', views.cardmarker_list_view, name='cardmarker_list'),
    path('cardmarkers/<int:pk>/password/', views.cardmarker_update_password, name='cardmarker_update_password'),
    path('cardmarkers/<int:pk>/delete/', views.cardmarker_delete, name='cardmarker_delete'),

    # Custom separate login pages
    path('login/admin/', views.AdminLoginView.as_view(), name='login_admin'),
    path('login/cardmark/', views.CardMarkLoginView.as_view(), name='login_cardmark'),

    # Standard auth URLs (logout, password reset, password change)
    path('', include('django.contrib.auth.urls')),
    path('cardmarkers/<int:pk>/delete/', views.cardmarker_delete, name='cardmarker_delete'),
]


