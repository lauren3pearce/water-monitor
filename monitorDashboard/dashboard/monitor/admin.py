from django.contrib import admin
from .models import WaterData, Alert, UserSettings

admin.site.register(WaterData)
admin.site.register(Alert)
admin.site.register(UserSettings)