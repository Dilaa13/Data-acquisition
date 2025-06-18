import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === Helper Function to Load CSV with strict parsing ===
def load_csv(path):
    with open(path, 'r') as file:
        raw_lines = file.readlines()[1:]  # Skip PuTTY-style header

    rows, temps, volts = [], [], []
    for idx, line in enumerate(raw_lines):
        parts = line.strip().split(',')
        if len(parts) >= 3:
            try:
                row = int(parts[0])
                temp = float(parts[1])
                volt = float(parts[2])
                # Only append when all three conversions succeed
                rows.append(row)
                temps.append(temp)
                volts.append(volt)
            except ValueError:
                continue  # Skip bad line

    df = pd.DataFrame({
        'Row': rows,
        'DS18B20_Temp_C': temps,
        'Thermistor_Voltage_V': volts
    })
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    return df.dropna()

# === File Paths ===
heat_path = 'D:/projects github/Data-acquisition/thermister02/Data_Analyse/heating_up.csv'
cool_path = 'D:/projects github/Data-acquisition/thermister02/Data_Analyse/cooling.csv'

# === Load Cleaned Data ===
df_heat = load_csv(heat_path)
df_cool = load_csv(cool_path)

# === Plot Raw Data for Both with Dots ===
plt.figure(figsize=(10, 6))

# Heating data points
plt.scatter(df_heat['DS18B20_Temp_C'], df_heat['Thermistor_Voltage_V'],
            label='Heating', color='red', s=8)

# Cooling data points
plt.scatter(df_cool['DS18B20_Temp_C'], df_cool['Thermistor_Voltage_V'],
            label='Cooling', color='blue', s=8)

plt.xlabel('DS18B20 Temperature (°C)')
plt.ylabel('Thermistor Voltage (V)')
plt.title('Thermistor Voltage vs Temperature (Heating vs Cooling)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

