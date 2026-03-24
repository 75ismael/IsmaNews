from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.contrib.auth.models import User
# classe Newspaper ( Edition ou Journal )
class Newspaper(models.Model):
    name = models.CharField(max_length=100) # ex: IsmaNews Afrique
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    color_code = models.CharField(max_length=7, default="#bc0000") # Pour le design du journal
    # Le filtre géographique.
    target_country = models.CharField(max_length=10, choices=[
        ('KM', 'Comores'), 
        ('FR', 'France'), 
        ('AF', 'Afrique'), 
        ('MO', 'Moyen-Orient'), 
        ('EUR', 'Europe'), 
        ('AS', 'Asie'), 
        ('AM', 'Amériques'),
        ('INT', 'International')
    ], default='INT')

    class Meta:
        verbose_name = "Journal"
        verbose_name_plural = "Journaux"

    def __str__(self):
        return self.name





class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Ex: fa-stethoscope")
    # Modifie cette ligne dans la classe Article
    #slug = models.SlugField(max_length=300, unique=False, null=True, blank=True)
    # On autorise le vide et on retire UNIQUE temporairement
    #slug = models.SlugField(max_length=300, unique=False, null=True, blank=True)
    # On autorise le vide et on retire UNIQUE temporairement
    #slug = models.SlugField(max_length=300, unique=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("review", "En révision"),
        ("published", "Publié")
    ]

    # --- LIAISON MULTI-JOURNAUX ---
    newspaper = models.ForeignKey(Newspaper, on_delete=models.CASCADE, related_name="articles", null=True)
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True, null=True)
    summary = models.TextField()
    content = models.TextField()
    
    # --- OPTIONS DE MISE EN AVANT (Pour ton plan visuel) ---
    is_breaking_news = models.BooleanField(default=False) # Pour le bandeau rouge clignotant
    is_ai_selection = models.BooleanField(default=False)  # Pour le bloc "Sélection IA"
    is_headline = models.BooleanField(default=False)      # Pour la grande "Une"
    is_audio_news = models.BooleanField(default=False)    # Pour la section Audio/Podcast
    audio_duration = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: 14 min écoute")
    audio_url = models.URLField(max_length=500, blank=True, null=True, help_text="Lien vers le fichier MP3 ou le flux audio")
    
    source = models.CharField(max_length=200, blank=True, null=True)
    source_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    # RELATIONS
    author = models.ForeignKey("AuthorProfile", on_delete=models.PROTECT, related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="articles")
    tags = models.ManyToManyField("Tag", blank=True)
    
    # STATS & STATUS
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    views = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.newspaper.name if self.newspaper else 'Sans Journal'}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-published_at']


# =====================================================
# 1️⃣ UTILISATEURS & SÉCURITÉ
# =====================================================

class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    photo = models.ImageField(upload_to="authors/", null=True)

class EditorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    def __str__(self):
        return self.user

class ReaderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class UserVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    verified = models.BooleanField(default=False)

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

# =====================================================
# 2️⃣ RÉDACTION
# =====================================================



class Tag(models.Model):
    name = models.CharField(max_length=50)

class Media(models.Model):
    file = models.FileField(upload_to="media/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Draft(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now=True)

class ArticleRevision(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

class Approval(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    editor = models.ForeignKey(EditorProfile, on_delete=models.CASCADE)
    approved = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

class Schedule(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    publish_date = models.DateTimeField()

class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class ArticleMedia(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)

# =====================================================
# 3️⃣ INTERACTION
# =====================================================

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class View(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now_add=True)

class Share(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)

class Bookmark(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Report(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reason = models.TextField()

# =====================================================
# 4️⃣ IA & ANALYTICS
# =====================================================

class AIArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AIRequest(models.Model):
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Trending(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    score = models.FloatField()

class SearchLog(models.Model):
    query = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

class TrafficStats(models.Model):
    date = models.DateField()
    visits = models.IntegerField()

class Revenue(models.Model):
    date = models.DateField()
    amount = models.FloatField()

# =====================================================
# 5️⃣ NEWSLETTER
# =====================================================

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    unsubscribe_token = models.CharField(max_length=64, blank=True)
    wants_daily = models.BooleanField(default=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = get_random_string(64)
        if not self.unsubscribe_token:
            self.unsubscribe_token = get_random_string(64)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
