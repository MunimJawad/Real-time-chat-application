from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #override default fields
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)

    #Presence 
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}---{self.email}"
    
class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    
    #images
    profile_photo = models.ImageField(upload_to='profiles/', default='images/default_profile.png', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='covers/', default='images/default_profile.png', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

