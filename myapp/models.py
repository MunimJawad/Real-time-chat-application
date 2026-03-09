from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name="rooms")

    def __str__(self):
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(max_length=20)
    stock = models.PositiveIntegerField(max_length=20)

    def __str__(self):
        return f"{self.name}"
    
class Order(models.Model):
    product = models.ForeignKey(Product,related_name='orders', on_delete=models.CASCADE)
    quantity = models.IntegerField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)