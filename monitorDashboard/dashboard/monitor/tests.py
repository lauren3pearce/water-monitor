from django.test import TestCase
from django.contrib.auth.models import User
from .models import WaterData, Alert, UserSettings

class AlertLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.settings = UserSettings.objects.create(
            user=self.user,
            low_water_threshold=100,
            high_conductivity_threshold=300,
            notify_low_water=True,
            notify_high_conductivity=True,
            notify_weekly_summary=False
        )

    def test_low_water_triggers_alert(self):
        reading = WaterData.objects.create(
            user=self.user,
            water_level=50,  # below threshold
            conductivity=100
        )
        if self.settings.notify_low_water and reading.water_level < self.settings.low_water_threshold:
            Alert.objects.create(user=self.user, message="Water level too low", level="Warning")

        self.assertEqual(Alert.objects.count(), 1)
        self.assertEqual(Alert.objects.first().message, "Water level too low")

    def test_high_conductivity_triggers_alert(self):
        reading = WaterData.objects.create(
            user=self.user,
            water_level=150,
            conductivity=400  # above threshold
        )
        if self.settings.notify_high_conductivity and reading.conductivity > self.settings.high_conductivity_threshold:
            Alert.objects.create(user=self.user, message="Conductivity too high", level="Warning")

        self.assertEqual(Alert.objects.count(), 1)
        self.assertEqual(Alert.objects.first().message, "Conductivity too high")

    def test_no_alert_when_notifications_disabled(self):
        self.settings.notify_low_water = False
        self.settings.notify_high_conductivity = False
        self.settings.save()

        reading = WaterData.objects.create(
            user=self.user,
            water_level=10,  # below threshold
            conductivity=500  # above threshold
        )

        # Simulate alert logic
        if self.settings.notify_low_water and reading.water_level < self.settings.low_water_threshold:
            Alert.objects.create(user=self.user, message="Water level too low", level="Warning")
        if self.settings.notify_high_conductivity and reading.conductivity > self.settings.high_conductivity_threshold:
            Alert.objects.create(user=self.user, message="Conductivity too high", level="Warning")

        self.assertEqual(Alert.objects.count(), 0)

    def test_user_settings_persistence(self):
        settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(settings.low_water_threshold, 100)
        self.assertEqual(settings.reading_interval_seconds, 30)

        # Update and test again
        settings.reading_interval_seconds = 60
        settings.save()

        updated = UserSettings.objects.get(user=self.user)
        self.assertEqual(updated.reading_interval_seconds, 60)

    def test_water_data_saves_correctly(self):
        WaterData.objects.create(
            user=self.user,
            water_level=200,
            conductivity=150
        )
        data = WaterData.objects.first()
        self.assertEqual(data.user.username, 'testuser')
        self.assertEqual(data.water_level, 200)
        self.assertEqual(data.conductivity, 150)

    def test_weekly_summary_toggle(self):
        self.settings.notify_weekly_summary = True
        self.settings.save()
        self.assertTrue(UserSettings.objects.get(user=self.user).notify_weekly_summary)
        
    def test_multiple_alerts_from_single_reading(self):
        reading = WaterData.objects.create(
            user=self.user,
            water_level=10,        # below threshold
            conductivity=500       # above threshold
        )

        if self.settings.notify_low_water and reading.water_level < self.settings.low_water_threshold:
            Alert.objects.create(user=self.user, message="Water level too low", level="Warning")

        if self.settings.notify_high_conductivity and reading.conductivity > self.settings.high_conductivity_threshold:
            Alert.objects.create(user=self.user, message="Conductivity too high", level="Warning")

        self.assertEqual(Alert.objects.count(), 2)
        messages = [a.message for a in Alert.objects.all()]
        self.assertIn("Water level too low", messages)
        self.assertIn("Conductivity too high", messages)

    def test_alert_timestamp_is_auto_set(self):
        Alert.objects.create(user=self.user, message="Test alert", level="Warning")
        alert = Alert.objects.first()
        self.assertIsNotNone(alert.timestamp)
        
    def test_water_data_str_output(self):
        reading = WaterData.objects.create(
            user=self.user,
            water_level=123,
            conductivity=321
        )
        expected = f"{reading.timestamp} - Level: 123, Cond: 321"
        self.assertEqual(str(reading), expected)
        
    def test_alert_str_output(self):
        alert = Alert.objects.create(
            user=self.user,
            message="Test Alert",
            level="Critical"
        )
        expected = f"{alert.timestamp} - {self.user.username} - Test Alert"
        self.assertEqual(str(alert), expected)
        
    def test_user_settings_user_link(self):
        settings = UserSettings.objects.get(user=self.user)
        self.assertEqual(settings.user.username, 'testuser')
        