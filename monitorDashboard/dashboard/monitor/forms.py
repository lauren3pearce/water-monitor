from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserSettings

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'low_water_threshold', 
            'high_conductivity_threshold', 
            'reading_interval_seconds',
            'notify_low_water',
            'notify_high_conductivity',
            'notify_weekly_summary'
        ]
        labels = {
            'low_water_threshold': 'Low Water Level Alert Threshold (%)',
            'high_conductivity_threshold': 'High Conductivity Alert Threshold (µS/cm)',
            'reading_interval_seconds': 'Reading Interval (seconds)',
            'notify_low_water': 'Email me for low water level alerts',
            'notify_high_conductivity': 'Email me for high conductivity alerts',
            'notify_weekly_summary': 'Email me a weekly summary',
        }