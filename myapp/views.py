from rest_framework.permissions import IsAdminUser
from rest_framework import serializers
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .models import Post, Comment, User, LikedPost, SavedPost, DepartmentSubscription, Notification
from .serializers import PostSerializer, UserSerializer, CommentSerializer, NotificationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [permissions.AllowAny]

class PostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        return queryset

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostCommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        post = Post.objects.get(pk=post_id)
        serializer.save(author=self.request.user, post=post)

class LikePost(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = generics.get_object_or_404(Post, pk=pk)
        like, created = LikedPost.objects.get_or_create(user=request.user, post=post)
        
        if created:
            post.number_of_likes += 1
            post.save()
            return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            post.number_of_likes -= 1
            post.save()
            return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)

class SavePost(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = generics.get_object_or_404(Post, pk=pk)
        saved_post, created = SavedPost.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'message': 'Post saved'}, status=status.HTTP_201_CREATED)
        else:
            saved_post.delete()
            return Response({'message': 'Post unsaved'}, status=status.HTTP_200_OK)

class UserLikedPosts(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs['username']
        user = generics.get_object_or_404(User, username=username)
        return Post.objects.filter(likedpost__user=user).order_by('-likedpost__id')

class UserSavedPosts(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        if self.request.user.username != username:
             return Post.objects.none()
        user = generics.get_object_or_404(User, username=username)
        return Post.objects.filter(savedpost__user=user).order_by('-savedpost__id')


class ToggleDepartmentFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        department = request.data.get('department')

        if not department or department not in User.Department.values:
            return Response(
                {'error': 'Invalid department'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = DepartmentSubscription.objects.get_or_create(
            user=request.user,
            department=department
        )

        if created:
            return Response(
                {
                    'department': department,
                    'following': True
                },
                status=status.HTTP_200_OK
            )

        subscription.delete()
        return Response(
            {
                'department': department,
                'following': False
            },
            status=status.HTTP_200_OK
        )
        
@api_view(["POST"])
def social_login(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email required"}, status=400)
    user, created = User.objects.get_or_create(
        email=email, defaults={"username": email.split("@")[0]}
    )
    # Optionally: return a JWT if your frontend expects it
    return Response({"success": True, "user_id": user.id})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def NotificationsView(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    


from rest_framework.exceptions import APIException
from django.http import JsonResponse
import traceback

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://cse-news-letter.vercel.app"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            from django.http import HttpResponse
            import json
            error_data = {
                'error': 'Google login failed',
                'details': str(e),
                'trace': tb
            }
            return HttpResponse(json.dumps(error_data), content_type='application/json', status=400)


# New view to update user role
class UpdateUserRoleView(APIView):

    class InputSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=User.Role.choices)

    def post(self, request, username):
        user = generics.get_object_or_404(User, username=username)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.role = serializer.validated_data['role']
        user.save(update_fields=['role'])
        return Response({'message': f"Role updated to {user.role}"})
    
class FollowedDepartmentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        followed = DepartmentSubscription.objects.filter(user_id=user_id).values_list('department', flat=True)
        return Response(list(followed))
class FollowedDepartmentsPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        followed_departments = DepartmentSubscription.objects.filter(
            user=self.request.user
        ).values_list('department', flat=True)
        return Post.objects.filter(department__in=followed_departments).order_by('-created_at')