from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Article, AuthorProfile, EditorProfile, 
    Comment, View, Subscription, Approval, Tag, Trending
)

# --- ACTIONS DE MASSE ---
@admin.action(description='🚀 Publier les articles sélectionnés')
def make_published(modeladmin, request, queryset):
    queryset.update(status='published')

# --- CONFIGURATION DES ARTICLES ---
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Colonnes de la liste
    list_display = ('title', 'display_category', 'author_link', 'status', 'view_count_colored', 'published_at')
    list_filter = ('status', 'category', 'published_at', 'author')
    # Recherche étendue (titre, contenu, nom de l'auteur et de la catégorie)
    search_fields = ('title', 'content', 'author__user__username', 'category__name')
    prepopulated_fields = {'slug': ('title',)}
    actions = [make_published]
    
    # Organisation de la page d'édition (layout)
    fieldsets = (
        ('Contenu Rédactionnel', {
            'fields': ('title', 'slug', 'category', 'summary', 'content'),
            'description': 'Rédigez ici le cœur de votre article.'
        }),
        ('Équipe & Validation', {
            'fields': ('author', 'status', 'published_at'),
            'classes': ('collapse',), # Masquable par défaut
        }),
        ('Médias & Référencement', {
            'fields': ('image_url', 'source', 'source_url'),
        }),
    )

    def display_category(self, obj):
        return obj.category.name if obj.category else "-"
    display_category.short_description = "Rubrique"

    def author_link(self, obj):
        if obj.author:
            return format_html('<a href="/admin/journal/authorprofile/{}/change/">👤 {}</a>', 
                               obj.author.id, obj.author.user.username)
        return "-"
    author_link.short_description = "Rédacteur"

    def view_count_colored(self, obj):
        color = "#28a745" if obj.views > 1000 else "#fd7e14" if obj.views > 100 else "#6c757d"
        return format_html('<span style="background:{}; color:white; padding:3px 8px; border-radius:10px; font-size:11px;">{} vues</span>', 
                           color, obj.views)
    view_count_colored.short_description = "Performance"

# --- GESTION DES AUTEURS ---
@admin.register(AuthorProfile)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_photo', 'article_count')
    
    def show_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%; object-fit:cover;" />', obj.photo.url)
        return "N/A"
    show_photo.short_description = "Photo"
    
    def article_count(self, obj):
        # Utilise le related_name 'articles' défini dans ton modèle Article
        return obj.articles.count()
    article_count.short_description = "Total Articles"

# --- ANALYTICS & TRENDING ---
@admin.register(Trending)
class TrendingAdmin(admin.ModelAdmin):
    list_display = ('article', 'score', 'is_trending_now')
    
    def is_trending_now(self, obj):
        return obj.score > 75
    is_trending_now.boolean = True
    is_trending_now.short_description = "En Top ?"

# --- ENREGISTREMENT DES AUTRES MODULES ---
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(EditorProfile)
admin.site.register(Comment)
admin.site.register(Subscription)
admin.site.register(Approval)

# Personnalisation visuelle globale
admin.site.site_header = "ISMANEWS MANAGEMENT"
admin.site.site_title = "Admin IsmaNews"
admin.site.index_title = "Gestion des Opérations Média"