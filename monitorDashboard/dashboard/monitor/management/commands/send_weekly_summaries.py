from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from monitor.models import UserSettings, WaterData, Alert
from django.contrib.auth.models import User
from datetime import timedelta
from django.db.models import Avg


class Command(BaseCommand):
    help = 'Send weekly summary emails to users'

    def handle(self, *args, **kwargs):
        one_week_ago = timezone.now() - timedelta(days=7)

        for user in User.objects.all():
            try:
                settings_obj = UserSettings.objects.get(user=user)
            except UserSettings.DoesNotExist:
                continue

            if not settings_obj.notify_weekly_summary:
                continue

            data = WaterData.objects.filter(user=user, timestamp__gte=one_week_ago)
            alerts = Alert.objects.filter(user=user, timestamp__gte=one_week_ago)

            if not data.exists():
                continue

            avg_level = data.aggregate(Avg('water_level'))['water_level__avg']
            avg_conduct = data.aggregate(Avg('conductivity'))['conductivity__avg']

            subject = "Your Weekly Water Monitor Summary"
            message = (
                f"Hello {user.username},\n\n"
                f"Here's your summary for the past 7 days:\n"
                f"- Total Readings: {data.count()}\n"
                f"- Average Water Level: {avg_level:.2f}%\n"
                f"- Average Conductivity: {avg_conduct:.2f} µS/cm\n"
                f"- Alerts Triggered: {alerts.count()}\n\n"
                f"Stay hydrated! 💧"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )

        self.stdout.write(self.style.SUCCESS("Weekly summaries sent."))
