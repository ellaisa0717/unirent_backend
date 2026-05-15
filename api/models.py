from django.db import models
from django.contrib.auth.models import User 

class Item(models.Model):
    title = models.CharField(max_length=255) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True) 
    category = models.CharField(max_length=100, default='General') 
    status = models.CharField(max_length=50, default='Available')
    locker_label = models.CharField(max_length=10, blank=True, null=True)
    
    is_approved = models.BooleanField(default=False) 
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class RentalTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} rented {self.item.title}"