#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"

// === Pin Config ===
#define DS_PIN 15           // DS18B20 DQ pin
#define THERMISTOR_ADC 26   // GPIO26 = ADC0

// === Thermistor Parameters ===
#define BETA 3950.0
#define R0 8300          // Updated resistance at 28.6°C
#define T0 301.6          // Updated reference temperature in Kelvin (28.6°C)
#define R_FIXED 8600.0      // Fixed resistor in voltage divider

// === DS18B20 Functions ===
void ds18b20_pull_low() {
    gpio_set_dir(DS_PIN, GPIO_OUT);
    gpio_put(DS_PIN, 0);
}

void ds18b20_release() {
    gpio_set_dir(DS_PIN, GPIO_IN);
}

bool ds18b20_reset() {
    ds18b20_pull_low();
    sleep_us(480);
    ds18b20_release();
    sleep_us(70);
    bool presence = !gpio_get(DS_PIN);
    sleep_us(410);
    return presence;
}

void ds18b20_write_bit(bool bit) {
    ds18b20_pull_low();
    sleep_us(bit ? 6 : 60);
    ds18b20_release();
    sleep_us(bit ? 64 : 10);
}

bool ds18b20_read_bit() {
    ds18b20_pull_low();
    sleep_us(6);
    ds18b20_release();
    sleep_us(9);
    bool bit = gpio_get(DS_PIN);
    sleep_us(55);
    return bit;
}

void ds18b20_write_byte(uint8_t data) {
    for (int i = 0; i < 8; i++) {
        ds18b20_write_bit(data & 1);
        data >>= 1;
    }
}

uint8_t ds18b20_read_byte() {
    uint8_t value = 0;
    for (int i = 0; i < 8; i++) {
        if (ds18b20_read_bit()) value |= (1 << i);
    }
    return value;
}

float ds18b20_get_temperature() {
    if (!ds18b20_reset()) return -1000;

    ds18b20_write_byte(0xCC);  // Skip ROM
    ds18b20_write_byte(0x44);  // Convert T
    sleep_ms(750);

    if (!ds18b20_reset()) return -1000;

    ds18b20_write_byte(0xCC);  // Skip ROM
    ds18b20_write_byte(0xBE);  // Read Scratchpad

    uint8_t lsb = ds18b20_read_byte();
    uint8_t msb = ds18b20_read_byte();
    int16_t raw = (msb << 8) | lsb;
    return raw / 16.0f;
}

// === Thermistor Temperature Reading with Voltage & Resistance ===
float read_thermistor_temp(float* voltage_out, float* resistance_out) {
    adc_select_input(0); // ADC0
    uint16_t raw = adc_read(); // 0–4095
    float voltage = raw * 3.3f / 4095.0f;
    // Corrected resistance formula for thermistor on ADC pin:
    float resistance = R_FIXED * (3.3f - voltage) / voltage;

    *voltage_out = voltage;
    *resistance_out = resistance;

    float tempK = 1.0 / (1.0 / T0 + log(resistance / R0) / BETA);
    return tempK - 273.15;
}


// === Main Program ===
int main() {
    stdio_init_all();
    sleep_ms(3000);  // Wait for USB serial to open

    // Initialize DS18B20 pin
    gpio_init(DS_PIN);
    ds18b20_release();

    // Initialize ADC for thermistor
    adc_init();
    adc_gpio_init(THERMISTOR_ADC);

    while (true) {
        float voltage, resistance;
        float ds_temp = ds18b20_get_temperature();
        float therm_temp = read_thermistor_temp(&voltage, &resistance);

        printf("DS18B20 Temperature: %.1f °C\tThermistor Temperature: %.1f °C\n", ds_temp, therm_temp);
        printf("Thermistor Voltage: %.1f V\tResistance: %.1f Ω\n", voltage, resistance);

        sleep_ms(1000);
    }
}