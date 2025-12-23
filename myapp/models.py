from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    class Department(models.TextChoices):
        General = 'General'
        HR = 'HR'
        Dev = 'Development'
        UIUX = 'UI/UX'
        Design = 'Design'
        RelevRelex = 'Relev/Relex'
        Comm = 'Communication'
        Multimedia = 'Multimedia'

    class Role(models.TextChoices):
        President = 'President'
        VicePresident = 'Vice President'
        Manager = 'Manager'
        Assistant = 'Assistant'
        Member = 'Member'

    email = models.EmailField(unique=True)
    department = models.CharField(max_length=15, choices=Department.choices, default=Department.General)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.Member)
    image = models.ImageField(upload_to='user_images/' , blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.pk and not self.is_superuser:
            count = User.objects.filter(is_superuser=False).count()
            if count == 0:
                self.role = self.Role.President
            elif count == 1:
                self.role = self.Role.VicePresident
        super().save(*args, **kwargs)
    
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    department = models.CharField(max_length=15, choices=User.Department.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    number_of_likes = models.IntegerField(default=0)
    number_of_comments = models.IntegerField(default=0)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.author.role in [User.Role.Manager, User.Role.Assistant]:
                self.department = self.author.department
        super().save(*args, **kwargs)

    def get_likes_count(self):
        return self.likedpost_set.count()

    def get_comments_count(self):
        return self.comment_set.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class LikedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class SavedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class DepartmentSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    department = models.CharField(max_length=15, choices=User.Department.choices)

    class Meta:
        unique_together = ('user', 'department')

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_general_subscription(sender, instance, created, **kwargs):
    if created:
        DepartmentSubscription.objects.get_or_create(user=instance, department=User.Department.General)

