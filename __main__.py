#!/usr/bin/python3

import time
from sds011 import SDS011
import signal
import sys
import getopt
from datetime import datetime

# Default values
interval = 1  # Query the sensor every X minutes
serial_port = "/dev/ttyUSB0"  # Replace with your actual serial port

def print_help():
    print("Usage: __main__.py [options]")
    print("Options:")
    print("  -i, --interval <minutes>  Set the query interval in minutes (default: 1)")
    print("  -p, --port <serial_port>  Set the serial port for the sensor (default: /dev/ttyUSB0)")
    print("  -h, --help                Show this help message and exit")

def parse_arguments():
    global interval, serial_port
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:", ["help", "interval=", "port="])
    except getopt.GetoptError as err:
        print(err)
        print_help()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-i", "--interval"):
            interval = int(arg)
        elif opt in ("-p", "--port"):
            serial_port = arg

parse_arguments()

# Define thresholds and labels - European Air Quality Index (EAQI)
PM25_THRESHOLDS = [10, 20, 25, 50, 75, 800]
PM10_THRESHOLDS = [20, 40, 50, 100, 150, 955]  # Maximum should be 1200, but the sensor only goes up to 999
LABELS = ['good', 'fair', 'moderate', 'poor', 'very poor', 'extremely poor', 'off the chart']

COLORS = {
    'good': '\033[96m', #80E0E0
    'fair': '\033[92m', #50B894
    'moderate': '\033[93m', #FCE179
    'poor': '\033[91m', #FF8773
    'very poor': '\033[95m', #BE3349
    'extremely poor': '\033[35m', #803C8E
    'off the chart': '\033[30;41m', #000000
    'reset': '\033[0m'
}

# Data
pm25_values, pm10_values = [], []
time_stamps = []

def get_label(value, thresholds, labels):
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return labels[i]
    return labels[-1]

def signal_handler(sig, frame):
    sensor.sleep(sleep=True)  # Put the sensor to sleep before exiting

    if pm25_values and pm10_values:
        avg_pm25 = sum(pm25_values) / len(pm25_values)
        avg_pm10 = sum(pm10_values) / len(pm10_values)
        avg_pm25_label = get_label(avg_pm25, PM25_THRESHOLDS, LABELS)
        avg_pm10_label = get_label(avg_pm10, PM10_THRESHOLDS, LABELS)
        
        avg_pm25_color = COLORS[avg_pm25_label]
        avg_pm10_color = COLORS[avg_pm10_label]
        
        bold, reset_bold = "\033[1m", "\033[22m"
        duration = datetime.now() - datetime.strptime(time_stamps[0], "%Y-%m-%d %H:%M")
        duration_hours, remainder = divmod(duration.total_seconds(), 3600)
        duration_minutes = remainder // 60
        print(f'\n\nAverage over {int(duration_hours)}h {int(duration_minutes)}m:\n'
              f'PM2.5: {bold}{avg_pm25:.1f} µg/m³{reset_bold} ({avg_pm25_color}{avg_pm25_label}{COLORS["reset"]})\n'
              f'PM10: {bold}{avg_pm10:.1f} µg/m³{reset_bold} ({avg_pm10_color}{avg_pm10_label}{COLORS["reset"]})\n')

    sys.exit(0)

print(f"SDS011 dust sensor")

# Initialize the sensor
sensor = SDS011(serial_port=serial_port)
time.sleep(1)
signal.signal(signal.SIGINT, signal_handler)  # Graceful exit
sensor.sleep(sleep=False)  # Wake the sensor up and start measuring
time.sleep(3)

print(f"Firmware Version: {sensor.check_firmware_version()}\n")
sensor.set_work_period(work_time=interval)

time.sleep(35) # Warm-up time

while True:
    try:
        pm25, pm10 = sensor.query()  # Query the sensor for PM2.5 and PM10 levels
        
        if pm25 and pm10:  # Ignore zero values
            pm25_values.append(pm25)
            pm10_values.append(pm10)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            time_stamps.append(current_time)
            pm25_label, pm10_label = get_label(pm25, PM25_THRESHOLDS, LABELS), get_label(pm10, PM10_THRESHOLDS, LABELS)
            
            print(f"{current_time}, PM2.5: {pm25:.1f} µg/m³ {COLORS[pm25_label]}{pm25_label}{COLORS['reset']}, "
                  f"PM10: {pm10:.1f} µg/m³ {COLORS[pm10_label]}{pm10_label}{COLORS['reset']}")

            if len(pm25_values) > 100:
                pm25_values.pop(0)
                pm10_values.pop(0)
                time_stamps.pop(0)

    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(interval * 60)
