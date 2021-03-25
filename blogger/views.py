from django.shortcuts import render
from django.http import HttpResponse

from .models import Blog


def get_blog_list(request):
    blogs = Blog.objects.order_by('title')
    return HttpResponse(
        '<ul>'
        + ''.join(['<li>%s</li>' % b.title for b in blogs])
        + '</ul>'

    )
