from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('api/register/', views.register_user, name='register_user'),
    path('api/login/', views.login_user, name='login_user'),
    path('api/logout/', views.logout_user, name='logout_user'),
    path('api/posts/', views.PostListView.as_view(), name='api_posts_list'),
    path('api/posts/create', views.PostCreateView.as_view(), name='api_posts_create'),
    path('post-detail/<int:id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('dashboard/post-detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post-edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post-delete/<int:post_id>/', views.delete_post, name='delete_post'),
]
