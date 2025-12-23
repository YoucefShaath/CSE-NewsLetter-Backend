# create_admin.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CSENewsletter.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    username = "admin" 
    email = "admin@example.com" 
    password = "12345678" 

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser for {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print("Superuser already exists.")

if __name__ == "__main__":
    create_superuser()