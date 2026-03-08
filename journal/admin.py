from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Article, AuthorProfile, EditorProfile, 
    Comment, View, Subscription, Approval, Tag, Trending,Newspaper
)


@admin.register(Newspaper)
class NewspaperAdmin(admin.ModelAdmin):
    # 1. On affiche plus d'infos dans la liste
    list_display = ('name', 'target_country', 'slug', 'color_preview', 'article_count')


    
    # 2. On ajoute des filtres qui font apparaître la barre à droite
    # Note: Filtrer par 'name' est peu utile, filtrer par date est mieux
    list_filter = ('target_country',)
    
    # 3. Recherche rapide
    search_fields = ('name', 'slug', 'target_country')
    
    # 4. Remplissage automatique du slug pendant la frappe
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('target_country', 'slug')

    # --- MÉTHODES PERSONNALISÉES ---

    def color_preview(self, obj):
        return format_html(
            '<div style="width:30px; height:20px; background:{}; border-radius:3px; border:1px solid #ccc;"></div>',
            obj.color_code
        )
    color_preview.short_description = "Couleur"

    def article_count(self, obj):
        # Affiche le nombre d'articles liés à ce journal
        return obj.articles.count()
    article_count.short_description = "Nb Articles"
    

# --- ACTIONS DE MASSE ---
@admin.action(description='🚀 Publier les articles sélectionnés')
def make_published(modeladmin, request, queryset):
    queryset.update(status='published')

# --- CONFIGURATION DES ARTICLES ---
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # On ajoute 'newspaper' et les badges de mise en avant
    list_display = ('title', 'newspaper', 'display_category', 'status', 'is_breaking', 'is_ai', 'published_at')
    list_filter = ('newspaper', 'status', 'category', 'is_breaking_news', 'is_ai_selection')
    search_fields = ('title', 'content', 'newspaper__name')
    prepopulated_fields = {'slug': ('title',)}
    actions = [make_published]
    
    fieldsets = (
        ('Journal & Rubrique', {
            'fields': ('newspaper', 'category', 'author'),
        }),
        ('Contenu Rédactionnel', {
            'fields': ('title', 'slug', 'summary', 'content'),
        }),
        ('Mise en Avant (Home Page)', {
            'fields': ('is_headline', 'is_breaking_news', 'is_ai_selection'),
            'description': 'Cochez ces cases pour afficher l\'article dans les sections spéciales du Home.'
        }),
        ('Médias & Référencement', {
            'fields': ('image_url', 'source', 'source_url', 'status', 'published_at'),
        }),
    )

    # Petites icônes visuelles pour la liste admin
    def is_breaking(self, obj):
        return obj.is_breaking_news
    is_breaking.boolean = True
    is_breaking.short_description = "🔥 Urgent"

    def is_ai(self, obj):
        return obj.is_ai_selection
    is_ai.boolean = True
    is_ai.short_description = "🧠 IA"

    def display_category(self, obj):
        return obj.category.name if obj.category else "-"
    display_category.short_description = "Rubrique"
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
