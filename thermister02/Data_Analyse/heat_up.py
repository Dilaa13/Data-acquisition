import serial
import time
import csv
import re

# === Config ===
port = 'COM14'           # Replace with your Pico's port
baudrate = 115200
csv_filename = 'sensor_data_up.csv'
flush_interval = 10  # seconds

# Updated regex patterns
ds_temp_pattern = re.compile(r"DS18B20 Temperature:\s*([-+]?\d*\.\d+|\d+)")
volt_pattern = re.compile(r"Thermistor Voltage:\s*([-+]?\d*\.\d+|\d+)")

try:
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for Pico to reset

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Row_Number', 'DS18B20_Temp_C', 'Thermistor_Voltage_V'])

        last_flush = time.time()
        ds_temp = None
        therm_volt = None
        row_number = 1  # Initialize counter

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue

            m1 = ds_temp_pattern.search(line)
            m2 = volt_pattern.search(line)

            if m1:
                ds_temp = float(m1.group(1))
            if m2:
                therm_volt = float(m2.group(1))

            if ds_temp is not None and therm_volt is not None:
                print(f"Row {row_number}, DS18B20: {ds_temp} °C, Voltage: {therm_volt} V")
                writer.writerow([row_number, ds_temp, therm_volt])
                row_number += 1

                if time.time() - last_flush >= flush_interval:
                    csvfile.flush()
                    last_flush = time.time()

                ds_temp = None
                therm_volt = None

except KeyboardInterrupt:
    print("\nExiting and closing serial port.")

finally:
    ser.close()
