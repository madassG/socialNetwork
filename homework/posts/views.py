from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.models import User

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow


@cache_page(20)
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
        form = PostForm(request.POST or None, files=request.FILES or None)

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

    following = False
    if request.user.is_authenticated and Follow.objects.filter(user=request.user, author=user):
        following = True

    return render(request, 'profile.html', {'user_p': user, 'page': page, 'following': following})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user)
    form = CommentForm()
    comments = post.comments.all()

    return render(request, 'post.html', {'author': user, 'post': post, 'form': form, 'comments': comments})


@login_required
def post_edit(request, username, post_id):
    if get_object_or_404(User, username=request.user.username) and request.user.username != username:
        return redirect('post', username, post_id)

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

        if form.is_valid():
            form.save()

            return redirect('post', username, post_id)

        return render(request, 'post_edit.html', {'form': form})
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            user = get_object_or_404(User, username=username)
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post, id=post_id, author = user)
            comment.save()
            return redirect('post', username, post_id)

    return redirect('post', username, post_id)


def page_not_found(request, exception):
    render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    render(request, 'misc/500.html', status=500)


@login_required
@cache_page(20)
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user).order_by('-pub_date')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()

    return redirect('profile', username)
