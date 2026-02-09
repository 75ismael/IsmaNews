from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include  # <-- include doit être importé
from journal import views  # si tu veux utiliser views directement


urlpatterns = [
    path("", views.home, name="home"),  # Accueil
    path("approve/<int:id>/", views.approve, name="approve"),  # Validation
    path("article/<int:id>/", views.article, name="article"),  # Lecture article
    path("category/<slug:slug>/", views.category, name="category"),  # Catégories
    path('search/', views.search, name='search'),
    
]

