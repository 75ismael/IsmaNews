from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
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

    title = models.CharField(max_length=300)
    # On aligne la taille du slug sur celle du titre
    slug = models.SlugField(max_length=300, unique=True, blank=True, null=True)
    summary = models.TextField()
    content = models.TextField()
    
    # --- LES CHAMPS MANQUANTS À RÉAJOUTER ---
    source = models.CharField(max_length=200, blank=True, null=True)
    source_url = models.URLField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    # ----------------------------------------

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
        return self.title

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
        return self.user

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
