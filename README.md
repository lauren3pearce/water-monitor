# Arduino-Based Water Monitoring System
This project is a real-time water monitoring system designed for small water bodies such as ponds or tanks. It uses an Arduino UNO R4 WiFi to measure water level and conductivity, sending the data to a Django-based web application for visualization, logging, and alerting. The system supports email notifications and weekly summary reports, with real-time graphs and a responsive dashboard.

## Features
- Real-time water level and conductivity monitoring
- Live display on LCD1602 (I2C)
- Visual alerts via LEDs
- USB Serial communication between Arduino and Django
- User authentication and personalized thresholds
- Real-time dashboard with interactive graphs (Plotly.js)
- Data filtering and CSV export
- Email alerts and weekly summaries (via Celery)

## Hardware Requirements
- Arduino UNO R4 WiFi
- Water Level Sensor (analog)
- Conductivity Sensor (analog)
- LCD1602 Display (with I2C adapter)
- 2x LEDs (for alerts)
- Breadboard and jumper wires
- USB cable for Arduino-PC connection

### INstall necessary packages: pip install -r requirements.txt 