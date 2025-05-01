import serial
import django
import os
import sys
import time


# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

from monitor.models import WaterData, UserSettings
from django.contrib.auth.models import User

arduino_port = "COM6"
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException as e:
    print(f"Error: {e}")
    sys.exit()

USERNAME = 'laurenp'
try:
    user = User.objects.get(username=USERNAME)
    settings = UserSettings.objects.get(user=user)
except Exception as e:
    print(f"Error getting user/settings: {e}")
    sys.exit()

# Send updated thresholds to Arduino
def send_thresholds():
    threshold_msg = f"THRESHOLDS:{settings.low_water_threshold},{settings.high_conductivity_threshold}\n"
    ser.write(threshold_msg.encode())
    print(f"Sent thresholds: {threshold_msg.strip()}")
    time.sleep(1)  # Give Arduino time to process

send_thresholds()

print("Reading Arduino data... (press Ctrl+C to stop)")
water_level = None
conductivity = None

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print("Raw:", line)

        if "Water Level:" in line:
            water_level = int(line.split(":")[1].strip())
        elif "Conductivity:" in line:
            conductivity = int(line.split(":")[1].strip())
            if water_level is not None:
                data = WaterData(user=user, water_level=water_level, conductivity=conductivity)
                data.save()
                print(f"Saved: WL={water_level}, Cond={conductivity}, Time={data.timestamp}")
except KeyboardInterrupt:
    print("Stopped.")
finally:
    ser.close()