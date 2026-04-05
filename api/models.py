from django.db import models

class Item(models.Model):
    title = models.CharField(max_length=255) 
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default='Available')
    locker_label = models.CharField(max_length=50) 
    owner_name = models.CharField(max_length=100) 
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.title