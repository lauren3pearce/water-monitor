import serial
import pandas as pd
import time
import matplotlib.pyplot as plt

# Configure the serial connection
arduino_port = "COM6"  
baud_rate = 9600       # Match the baud rate of my Arduino
log_file = "water_data.csv"

# Initialize serial connection
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

# Create a DataFrame to store logged data
columns = ["Timestamp", "Water Level", "Conductivity"]
data = pd.DataFrame(columns=columns)

# Function to log data
def log_data(water_level, conductivity):
    global data
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{"Timestamp": timestamp, "Water Level": water_level, "Conductivity": conductivity}])
    data = pd.concat([data, new_entry], ignore_index=True)
    data.to_csv(log_file, index=False)  # Save data to CSV file
    print(new_entry.iloc[0].to_dict())  # Print to console

# Function to plot data
def plot_data():
    if data.empty:
        print("No data to plot yet.")
        return
    plt.figure(figsize=(10, 5))
    plt.plot(data["Timestamp"], data["Water Level"], label="Water Level", marker="o")
    plt.plot(data["Timestamp"], data["Conductivity"], label="Conductivity", marker="o")
    plt.xlabel("Timestamp")
    plt.ylabel("Values")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Main loop to read and log data
print("Starting data logging. Press Ctrl+C to stop.")
try:
    while True:
        # Read a line of input from the Arduino
        line = ser.readline().decode("utf-8").strip()

        # Print the raw data received from the Arduino to debug
        print(f"Raw Data: {line}")

        # Parse the data
        if "Water Level:" in line:
            water_level = int(line.split(":")[1].strip())
        elif "Conductivity:" in line:
            conductivity = int(line.split(":")[1].strip())
            # Log the data only after both values are available
            log_data(water_level, conductivity)

except KeyboardInterrupt:
    print("Data logging stopped.")
    ser.close()
    plot_data()  # Plot data when logging stops
except Exception as e:
    print(f"Error: {e}")
    ser.close()