from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Follow
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    PostForm, CommentForm
)

# ---------- Custom Logout (instant, no confirmation page) ----------
def logout_view(request):
    auth_logout(request)
    return redirect('register')

# ---------- Registration ----------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# ---------- News Feed ----------
@login_required
def feed(request):
    following_users = request.user.following.values_list('following_id', flat=True)
    following_users = list(following_users) + [request.user.id]
    posts = Post.objects.filter(user__id__in=following_users).order_by('-created_at')
    return render(request, 'mediaapp/feed.html', {'posts': posts})

# ---------- Profile View ----------
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.posts.all()
    followers_count = user.followers.count()
    following_count = user.following.count()

    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    }
    return render(request, 'mediaapp/profile.html', context)

# ---------- Edit Profile ----------
@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'mediaapp/edit_profile.html', {'u_form': u_form, 'p_form': p_form})

# ---------- Create Post ----------
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'mediaapp/create_post.html', {'form': form})

# ---------- Edit Post ----------
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.user:
        messages.error(request, 'You cannot edit this post.')
        return redirect('feed')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('feed')
    else:
        form = PostForm(instance=post)
    return render(request, 'mediaapp/edit_post.html', {'form': form})

# ---------- Delete Post ----------
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.user:
        messages.error(request, 'You cannot delete this post.')
        return redirect('feed')
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('feed')

# ---------- Like / Unlike Post ----------
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

# ---------- Post Detail + Comments ----------
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added.')
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    return render(request, 'mediaapp/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

# ---------- Follow / Unfollow ----------
@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if request.user == user_to_follow:
        messages.error(request, "You cannot follow yourself.")
    else:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        messages.success(request, f'You are now following {username}')
    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'You have unfollowed {username}')
    return redirect('profile', username=username)

# ---------- Search Users ----------
def search_users(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(username__icontains=query) | User.objects.filter(profile__bio__icontains=query)
        users = users.distinct()
    else:
        users = User.objects.none()
    return render(request, 'mediaapp/search.html', {'users': users, 'query': query})