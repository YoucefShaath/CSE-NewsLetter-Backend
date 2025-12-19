from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<str:username>/liked/', views.UserLikedPosts.as_view(), name='user_liked_posts'),
    path('users/<str:username>/saved/', views.UserSavedPosts.as_view(), name='user_saved_posts'),
    path('posts/', views.PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('posts/<int:pk>/comments/', views.PostCommentList.as_view(), name='post_comment_list'),
    path('posts/<int:pk>/like/', views.LikePost.as_view(), name='like_post'),
    path('posts/<int:pk>/save/', views.SavePost.as_view(), name='save_post'),
    path('departments/follow/', views.ToggleDepartmentFollowView.as_view(), name='toggle_department_follow'),
]