from django.contrib import admin
from django.urls import path, include
from journal import views  # Assure-hui que 'journal' est bien le nom de ton dossier app

urlpatterns = [
    # --- ACCUEIL GLOBAL ---
    path("", views.home, name="home"),

    # --- MULTI-JOURNAUX (Navigation Globale) ---
    path("edition/<slug:slug>/", views.home, name="newspaper_detail"),

    # --- ARTICLES & NAVIGATION ---
    path("article/<int:id>/", views.article, name="article"),
    path("category/<slug:category_slug>/", views.category, name="category"),
    path("edition/<slug:edition_slug>/category/<slug:category_slug>/", views.category, name="category_in_edition"),
    path('search/', views.search, name='search'),

    # --- ADMINISTRATION & VALIDATION ---
    path("unsubscribe/<str:email>/<str:token>/", views.unsubscribe_newsletter, name="unsubscribe_newsletter"),
    path("subscribe/verify/<str:token>/", views.verify_newsletter, name="verify_newsletter"),
    path("subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),
    path("approve/<int:id>/", views.approve, name="approve"),
    path("signup/", views.signup, name="signup"),
]
