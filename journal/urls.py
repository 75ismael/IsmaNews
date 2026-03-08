from django.contrib import admin
from django.urls import path, include
from journal import views  # Assure-hui que 'journal' est bien le nom de ton dossier app

urlpatterns = [
    # --- ACCUEIL GLOBAL ---
    path("", views.home, name="home"),

    # --- MULTI-JOURNAUX (Ce qui manquait) ---
    # Cette ligne permet d'accéder à /journal/comores/ ou /journal/afrique/
    path("journal/<slug:slug>/", views.newspaper_detail, name="newspaper_detail"),

    # --- ARTICLES & NAVIGATION ---
    path("article/<int:id>/", views.article, name="article"),
    path("category/<slug:slug>/", views.category, name="category"),
    path('search/', views.search, name='search'),

    # --- ADMINISTRATION & VALIDATION ---
    path("approve/<int:id>/", views.approve, name="approve"),
    path('admin/', admin.site.urls),
]
