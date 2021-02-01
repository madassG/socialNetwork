from .models import Post, Group
from users.models import User
from .forms import PostForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# @login_required
def index(request):
    latest = Post.objects.order_by('-pub_date')

    paginator = Paginator(latest, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


# @login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    latest = Post.objects.order_by('-pub_date').filter(group=group)

    paginator = Paginator(latest, 10)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


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

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})
    # form_class = PostForm
    # success_url = reverse_lazy("index")
    # template_name = "new_post.html"


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.order_by('-pub_date').filter(author=user)

    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'user_p': user, 'page': page})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=user).count()

    return render(request, 'post.html', {'author': user, 'post': post, 'posts_count': posts_count})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('/'+str(username)+'/'+str(post_id)+'/')

    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.save()

            return redirect('/'+str(username)+'/'+str(post_id)+'/')

        return render(request, 'post_edit.html', {'form': form})
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})
