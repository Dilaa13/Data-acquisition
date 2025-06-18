import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial

# Load updated cooling and heating data
cooling_df = pd.read_csv('D:/projects github/Data-acquisition/thermister02/Data_Analyse/cooling.csv', header=None, names=['Row', 'Temp', 'Volt'])     #path for the cooling.csv
heating_df = pd.read_csv('D:/projects github/Data-acquisition/thermister02/Data_Analyse/heating_up.csv', header=None, names=['Row', 'Temp', 'Volt'])  #path for the heating_up.csv

# Clean data
cooling_df.replace([np.inf, -np.inf], np.nan, inplace=True)
heating_df.replace([np.inf, -np.inf], np.nan, inplace=True)
cooling_df.dropna(inplace=True)
heating_df.dropna(inplace=True)

# Fit 2nd-degree polynomials
cooling_fit = Polynomial.fit(cooling_df['Temp'], cooling_df['Volt'], 3)
heating_fit = Polynomial.fit(heating_df['Temp'], heating_df['Volt'], 3)

# Evaluate fits
cooling_pred = cooling_fit(cooling_df['Temp'])
heating_pred = heating_fit(heating_df['Temp'])

# Compute residuals
cooling_resid = cooling_df['Volt'] - cooling_pred
heating_resid = heating_df['Volt'] - heating_pred

# Plot residuals
plt.figure(figsize=(10, 6))
plt.scatter(cooling_df['Temp'], cooling_resid, color='blue', label='Cooling Residuals (3rd deg)', s=10)
plt.scatter(heating_df['Temp'], heating_resid, color='red', label='Heating Residuals (3rd deg)', s=10)
plt.axhline(0, color='black', linestyle='--', linewidth=1)
plt.xlabel('DS18B20 Temperature (°C)')
plt.ylabel('Residual (V)')
plt.title('Residuals using 3rd Degree Polynomial Fit')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
