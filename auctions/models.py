from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.categoryName}"
    
class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_bids")

    def __str__(self):
        return f"{self.bid}"    

class List(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=300)
    imageUrl = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="list_prices")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    listing = models.ForeignKey(List, on_delete=models.CASCADE, null=True, related_name="comments")
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username}: {self.comment}"




