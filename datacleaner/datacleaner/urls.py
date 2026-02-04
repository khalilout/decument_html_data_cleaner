"""
URL configuration for datacleaner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from . import views  # 👈 Import des vues depuis le même dossier

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirection de la page d'accueil vers /upload/
    path('', RedirectView.as_view(url='/upload/', permanent=False)),
    
    # Routes de l'application
    path('upload/', views.index, name='index'),
    path('upload/process/', views.upload, name='upload_file'),
    path('download/', views.download, name='download_cleaned'),
]