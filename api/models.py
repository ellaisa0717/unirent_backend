from django.db import models
from django.contrib.auth.models import User 

class Item(models.Model):
    title = models.CharField(max_length=255) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default='Available')
    locker_label = models.CharField(max_length=50) 
    
   # Updated: Links the item to a specific User (Student) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items') 
    
    is_approved = models.BooleanField(default=False) 
    
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Owned by {self.owner.username})"

class RentalTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} rented {self.item.title}"