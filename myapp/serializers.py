from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Post, Comment, LikedPost, SavedPost, User

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save(update_fields=['first_name', 'last_name'])

class UserSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'department', 'role', 'image', 'subscriptions']

    def get_subscriptions(self, obj):
        return list(obj.subscriptions.values_list('department', flat=True))

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    department = serializers.ChoiceField(choices=User.Department.choices, required=False)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.role not in [User.Role.Manager, User.Role.Assistant]:
                if 'department' not in data or not data['department']:
                     raise serializers.ValidationError({"department": "This field is required."})
        return data

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def get_comments_count(self, obj):
        return obj.get_comments_count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LikedPost.objects.filter(post=obj, user=request.user).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedPost.objects.filter(post=obj, user=request.user).exists()
        return False
