import serial
import time
import csv
import re

# === Config ===
port = 'COM14'           # Replace with your Pico's COM port
baudrate = 115200
csv_filename = 'sensor_data_up.csv'
flush_interval = 10      # Seconds

# Regex patterns to extract float numbers from the two lines
temp_pattern = re.compile(r"DS18B20 Temperature:\s*([-+]?\d*\.\d+|\d+) °C\s+Thermistor Temperature:\s*([-+]?\d*\.\d+|\d+) °C")
volt_res_pattern = re.compile(r"Thermistor Voltage:\s*([-+]?\d*\.\d+|\d+) V\s+Resistance:\s*([-+]?\d*\.\d+|\d+) Ω")

try:
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Wait for Pico reset

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(['Timestamp', 'DS18B20_Temp_C', 'Thermistor_Temp_C', 'Thermistor_Voltage_V', 'Thermistor_Resistance_Ohms'])

        last_flush = time.time()

        buffer = []

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue

            buffer.append(line)

            # When buffer has 2 lines (as your Pico outputs 2 lines per reading)
            if len(buffer) == 2:
                # Try to parse the two lines
                m1 = temp_pattern.match(buffer[0])
                m2 = volt_res_pattern.match(buffer[1])

                if m1 and m2:
                    ds_temp = float(m1.group(1))
                    therm_temp = float(m1.group(2))
                    therm_volt = float(m2.group(1))
                    therm_res = float(m2.group(2))
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Print to console for debug (optional)
                    print(f"{timestamp}, DS18B20: {ds_temp}, Thermistor Temp: {therm_temp}, Voltage: {therm_volt}, Resistance: {therm_res}")

                    # Write row to CSV
                    writer.writerow([timestamp, ds_temp, therm_temp, therm_volt, therm_res])

                    # Flush periodically
                    if time.time() - last_flush >= flush_interval:
                        csvfile.flush()
                        last_flush = time.time()
                else:
                    print("Warning: Failed to parse lines:")
                    print(buffer[0])
                    print(buffer[1])

                # Clear buffer for next reading
                buffer = []

except KeyboardInterrupt:
    print("\nExiting and closing serial port.")

finally:
    ser.close()
