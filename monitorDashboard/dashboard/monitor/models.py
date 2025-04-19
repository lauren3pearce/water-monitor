from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class WaterData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    water_level = models.IntegerField()
    conductivity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - Level: {self.water_level}, Cond: {self.conductivity}"
    
class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    level = models.CharField(max_length=20, default='Warning')  # e.g. 'Warning', 'Critical'

    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.message}"
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    low_water_threshold = models.IntegerField(default=20)
    high_conductivity_threshold = models.IntegerField(default=200)
    reading_interval_seconds = models.IntegerField(default=30)

    # email notifications
    notify_low_water = models.BooleanField(default=False)
    notify_high_conductivity = models.BooleanField(default=False)
    notify_weekly_summary = models.BooleanField(default=False)

    def __str__(self):
        return f"Settings for {self.user.username}"
    