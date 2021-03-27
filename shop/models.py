from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import *
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Product(Model):
    title = CharField(max_length=80)
    description = CharField(max_length=4096)
    price = IntegerField('price of product')

    averageRating = FloatField('average rating', default=-1)

    def __str__(self):
        return str(self.title)


class Review(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    textPositive = TextField(max_length=4096)
    textNegative = TextField(max_length=4096)
    textSummary = TextField(max_length=4096)
    username = TextField(max_length=30)
    city = TextField(max_length=40)
    rating = models.CharField(max_length=1, choices=[
                                ('1', 'terrible'),
                                ('2', 'bad'),
                                ('3', 'average'),
                                ('4', 'good'),
                                ('5', 'perfect')]
                              )

    created_at = DateTimeField('creation timestamp', auto_now_add=True)
    updated_at = DateTimeField('update timestamp', auto_now=True)
    reviewLikes = IntegerField('the number of users who think the review is useful')
    reviewDislikes = IntegerField('the number of users who think the review is useless')

    author = ForeignKey(User, on_delete=CASCADE, default=1)

    def __str__(self):
        return str(self.product.title + ' review')


class ReviewComment(Model):
    author = ForeignKey(User, on_delete=CASCADE, default=1)
    product = ForeignKey(Product, on_delete=CASCADE, default=1)
    review = ForeignKey(Review, on_delete=CASCADE)
    text = TextField(max_length=4096)
    username = TextField(max_length=30)
    created_at = DateTimeField('creation timestamp', auto_now_add=True)
    updated_at = DateTimeField('update timestamp', auto_now=True)

    def __str__(self):
        return str('comment')


class ShopCart(Model):
    author = ForeignKey(User, on_delete=CASCADE, default=1)
    products = ArrayField(models.IntegerField(), blank=True)


class Sentiment(Model):
    author = ForeignKey(User, on_delete=CASCADE)
    review = ForeignKey(Review, on_delete=CASCADE)
    vote = IntegerField('like = 1; dislike = -1', default=0)