from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, DepartmentSubscription, Notification

@receiver(post_save, sender=Post)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        author_department = instance.department
        # Find users subscribed to this department
        subscriptions = DepartmentSubscription.objects.filter(department=author_department)
        
        notifications = []
        for sub in subscriptions:
            # Don't notify the author themselves
            if sub.user != instance.author:
                notifications.append(
                    Notification(
                        recipient=sub.user,
                        post=instance
                    )
                )
        
        Notification.objects.bulk_create(notifications)
