from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Like, Follow
from .serializers import (
    ProfileSerializer, PostSerializer, CommentSerializer, UserSerializer
)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        return user.profile

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if request.user != profile.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user != post.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            Like.objects.get_or_create(user=request.user, post=post)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Like.objects.filter(user=request.user, post=post).delete()
            return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(user=self.request.user, post=post)

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        comment = self.get_object()
        if request.method == 'POST':
            Like.objects.get_or_create(user=request.user, comment=comment)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Like.objects.filter(user=request.user, comment=comment).delete()
            return Response({'status': 'unliked'}, status=status.HTTP_204_NO_CONTENT)

class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def follow(self, request, user_id=None):
        user_to_follow = get_object_or_404(User, id=user_id)
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        return Response({'status': 'following'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def unfollow(self, request, user_id=None):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        return Response({'status': 'unfollowed'}, status=status.HTTP_204_NO_CONTENT)

class SearchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        query = request.GET.get('query', '')
        if query:
            users = User.objects.filter(username__icontains=query) | User.objects.filter(profile__bio__icontains=query)
            users = users.distinct()
        else:
            users = User.objects.none()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)