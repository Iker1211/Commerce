from django.contrib import admin
from .models import User, Category, List, Comment
from .models import Bid
# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(List)
admin.site.register(Comment)
admin.site.register(Bid)


