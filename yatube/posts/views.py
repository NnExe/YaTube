from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, GroupForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import my_paginator


@cache_page(settings.CACHE_TIME)
def index(request):
    posts = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = my_paginator(posts, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author").all()
    page_number = request.GET.get('page')
    page_obj = my_paginator(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'is_group_page': True,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related("group").all()
    page_number = request.GET.get('page')
    page_obj = my_paginator(posts, page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user).filter(author=user).exists()
    else:
        following = False
    context = {
        'page_obj': page_obj,
        'no_author': True,
        'author': user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    num_posts = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.select_related(
        "author").select_related("post").filter(post=post)
    form = CommentForm()
    context = {
        'post': post,
        'num_posts': num_posts,
        'id': post_id,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
        'title': 'Добавить запись',
        'button_name': 'Добавить',
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        'form': form,
        'title': 'Редактировать запись',
        'button_name': 'Сохранить',
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author.username != request.user.username:
        return redirect("posts:post_detail", post_id)
    post.delete()
    return redirect('posts:profile', post.author.username)


@permission_required('posts.add_groups')
def group_create(request):
    form = GroupForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('posts:group_list', form.cleaned_data['slug'])
    context = {
        'form': form,
        'title': 'Добавить группу',
        'button_name': 'Добавить',
    }
    return render(request, 'posts/create_post.html', context)


@permission_required('posts.add_groups')
def group_edit(request, slug):
    group = get_object_or_404(Group, slug=slug)
    form = GroupForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        return redirect("posts:group_list", slug)
    context = {
        'form': form,
        'title': 'Редактировать группу',
        'button_name': 'Сохранить',
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followers = Follow.objects.filter(user=request.user)
    posts = Post.objects.filter(
        author__in=followers.values("author")
    )
    page_number = request.GET.get('page')
    page_obj = my_paginator(posts, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if ((not Follow.objects.filter(user=user).filter(
         author=author).exists()) and (author != user)):
        follower = Follow()
        follower.author = author
        follower.user = user
        follower.save()
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=user).filter(author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', author.username)