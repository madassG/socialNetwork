from django.shortcuts import render
from django.http import HttpResponse
from .models import Post, Group
from django.shortcuts import render, get_object_or_404


def index(request):
    latest = Post.objects.order_by('-pub_date')[:10]
    return render(request, 'index.html', {'posts': latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    latest = Post.objects.order_by('-pub_date').filter(group=group)[:12]
    return render(request, 'group.html', {'group': group, 'posts': latest})
