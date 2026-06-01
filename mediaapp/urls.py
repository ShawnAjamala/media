from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    ProfileViewSet, PostViewSet, CommentViewSet,
    FollowViewSet, SearchViewSet
)

# Frontend URLs
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # FIXED: custom logout – instant redirect to register
    path('logout/', views.logout_view, name='logout'),

    path('', views.feed, name='feed'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),

    path('post/new/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),

    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),

    path('search/', views.search_users, name='search'),
]

# API Router
router = DefaultRouter()
router.register(r'api/posts', PostViewSet, basename='post-api')
router.register(r'api/search/users', SearchViewSet, basename='search-api')

# Additional API routes
urlpatterns += [
    path('api/profiles/<int:user_id>/', ProfileViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='profile-api'),
    path('api/posts/<int:post_id>/comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-comments'),
    path('api/comments/<int:pk>/', CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='comment-detail'),
    path('api/comments/<int:pk>/like/', CommentViewSet.as_view({'post': 'like', 'delete': 'like'}), name='comment-like'),
    path('api/users/<int:user_id>/follow/', FollowViewSet.as_view({'post': 'follow', 'delete': 'unfollow'}), name='user-follow'),
]

urlpatterns += router.urls