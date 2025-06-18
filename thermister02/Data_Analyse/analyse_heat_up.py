import pandas as pd  # type: ignore
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit  # type: ignore

# === Step 1: Load raw file (comma-separated, PuTTY-style header) ===
file_path = 'D:/projects github/Data-acquisition/thermister02/Data Analyse/heating_up.csv'
with open(file_path, 'r') as file:
    raw_lines = file.readlines()[1:]  # Skip PuTTY header if present

# === Step 2: Parse lines using comma splitting ===
rows, temps, volts = [], [], []
for idx, line in enumerate(raw_lines):
    parts = line.strip().split(',')  # FIXED: comma-separated
    print(f"Line {idx+1}: '{line.strip()}'")
    print(f"Parsed parts: {parts}")

    if len(parts) >= 3:
        try:
            row = int(parts[0])
            temp = float(parts[1])
            volt = float(parts[2])
            rows.append(row)
            temps.append(temp)
            volts.append(volt)
        except ValueError:
            print(f"Skipping bad line {idx+1}: {parts}")
            continue
    else:
        print(f"Skipping incomplete line {idx+1}: {parts}")

# === Step 3: Create DataFrame and clean ===
df = pd.DataFrame({
    'Row': rows,
    'DS18B20_Temp_C': temps,
    'Thermistor_Voltage_V': volts
})
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

# Check if there's valid data before proceeding
if df.empty:
    print("❌ No valid data found after parsing and cleaning.")
    exit()

# === Step 4: Define and apply exponential fit ===
def exp_model(x, a, b, c):
    return a * np.exp(-b * x) + c

x = df['DS18B20_Temp_C'].values
y = df['Thermistor_Voltage_V'].values
popt, _ = curve_fit(exp_model, x, y, maxfev=10000)

# === Step 5: Plot ===
x_fit = np.linspace(min(x), max(x), 300)
y_fit = exp_model(x_fit, *popt)

plt.figure(figsize=(10, 6))
plt.scatter(x, y, label='Raw Data', color='blue', s=10)
plt.plot(x_fit, y_fit, color='red',
         label=f'Fitted: y = {popt[0]:.2f} * exp(-{popt[1]:.2f} * x) + {popt[2]:.2f}')
plt.xlabel('DS18B20 Temperature (°C)')
plt.ylabel('Thermistor Voltage (V)')
plt.title('Thermistor Voltage vs DS18B20 Temperature')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
