import serial
import django
import os
import sys

# Setup Django so we can access models
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')  # adjust if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')  # adjust if needed
django.setup()

from monitor.models import WaterData
from django.contrib.auth.models import User
from datetime import datetime

# Update this with your Arduino port
arduino_port = "COM6"
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException as e:
    print(f"Error: {e}")
    sys.exit()

# Replace this with the correct user in your system
USERNAME = 'laurenp'  # or your admin/test user

try:
    user = User.objects.get(username=USERNAME)
except User.DoesNotExist:
    print("User not found.")
    sys.exit()

water_level = None
conductivity = None

print("Reading Arduino data... (press Ctrl+C to stop)")
try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        print("Raw:", line)

        if "Water Level:" in line:
            water_level = int(line.split(":")[1].strip())
        elif "Conductivity:" in line:
            conductivity = int(line.split(":")[1].strip())

            if water_level is not None:
                # Save to DB
                data = WaterData(user=user, water_level=water_level, conductivity=conductivity)
                data.save()
                print(f"Saved: WL={water_level}, Cond={conductivity}, Time={data.timestamp}")

except KeyboardInterrupt:
    print("Stopped.")
finally:
    ser.close()
