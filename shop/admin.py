from django.contrib import admin
from . import models


admin.site.register(models.Product)
admin.site.register(models.Review)
admin.site.register(models.ReviewComment)
admin.site.register(models.ShopCart)
admin.site.register(models.Sentiment)