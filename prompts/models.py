from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.db.models import Avg

class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        default="avatars/default.png",

    )

    bio = models.TextField(
        max_length=300,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )




class Category(models.Model):
    name = models.CharField(max_length= 64)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


    class Meta:
        ordering = ["name"]


class Prompt(models.Model):

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"


    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'prompts')
    title = models.CharField(max_length= 200)
    content =models.TextField()
    description = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name= 'prompts')

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC
    )

    views = models.PositiveIntegerField(default=0)
    copies = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]






