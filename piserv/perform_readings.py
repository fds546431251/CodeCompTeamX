#!/home/zenbook/Development/.devenv/bin/python
import sensors as s
import sys
import time

GPIO_PIN = None
DB_IP = None

if len(sys.argv) != 3:
    print("Usage: ./perform_readings.py <GPIO pin number> <Database IP>")
    sys.exit(1)

else:
    try:
        GPIO_PIN = int(sys.argv[1])
        DB_IP = str(sys.argv[2])
    except ValueError as e:
        print("GPIO pin must be integer.")
try:
    while True:
        reading = s.getReading(GPIO_PIN, None)
        for key in reading.keys():
            s.addDatabaseEntry(reading[key], key, DB_IP)
        time.sleep(5)
except KeyboardInterrupt:
    print("Received keyboard interrupt. Stopping.")
    sys.exit(1)