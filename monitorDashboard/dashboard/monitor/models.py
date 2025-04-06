from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class WaterData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    water_level = models.FloatField()
    conductivity = models.FloatField()

    def __str__(self):
        return f"Water Level: {self.water_level}, Conductivity: {self.conductivity} at {self.timestamp}"
    
class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    level = models.CharField(max_length=20, default='Warning')  # e.g. 'Warning', 'Critical'

    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.message}"