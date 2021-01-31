from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Post, Group
from .forms import PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    latest = Post.objects.order_by('-pub_date')[:10]
    return render(request, 'index.html', {'posts': latest})


@login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    latest = Post.objects.order_by('-pub_date').filter(group=group)[:12]
    return render(request, 'group.html', {'group': group, 'posts': latest})


@login_required
def new_post(request):

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('index')

        return render(request, 'new_post.html', {'form': form})

    return render(request, 'new_post.html', {'form': PostForm})
    # form_class = PostForm
    # success_url = reverse_lazy("index")
    # template_name = "new_post.html"
