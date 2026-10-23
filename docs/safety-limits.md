# HeatSense Battery Safety Limits

> **CRITICAL ARCHITECTURAL DIRECTIVE:**
> No code may treat these limits as validated until the status column explicitly says CONFIRMED.
> All values below are provisional estimates subject to physical bench confirmation by the hardware teammate against the manufacturer datasheet.

---

## Safety Limits Table

The limits below represent firmware-enforced trip thresholds. When any confirmed limit is violated for longer than the debounce period, the ESP32 firmware autonomously opens the 5 V load isolation relay and enters a latched fault state.

| Parameter | Provisional Value | Status | Source Required | Owner | Date Confirmed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Over-Voltage (OV)** | 4.25 V | PROVISIONAL | Manufacturer cell datasheet (Samsung INR18650-25R) and hardware teammate bench confirmation | human | [not yet confirmed] |
| **Under-Voltage (UV)** | 2.80 V | PROVISIONAL | Manufacturer cell datasheet cut-off voltage specification under load | human | [not yet confirmed] |
| **Over-Temperature (OT, surface)** | 45.0 °C | PROVISIONAL | Cell thermal operating envelope datasheet and thermistor bench calibration | human | [not yet confirmed] |
| **Over-Current (OC, discharge)** | 2.0 A | PROVISIONAL | 10 ohm / 10 W load resistor rating (nominal 0.42 A at 4.2 V; 2.0 A accommodates fault surge) | human | [not yet confirmed] |
| **Sensor-Fault Timeout** | 500 ms | PROVISIONAL | INA219 I2C and DS18B20 1-Wire communication timeout tolerance | human | [not yet confirmed] |
| **Boot Self-Check Duration** | 1000 ms | PROVISIONAL | Relay interlock verification and initial sensor sanity check window | human | [not yet confirmed] |
| **Debounce Count (per limit)** | 3 consecutive samples | PROVISIONAL | Firmware noise rejection filter against electrical switching transients | human | [not yet confirmed] |

---

## Procedure for Confirming Limits

1. The hardware teammate obtains the official manufacturer specification sheet for the specific 18650 cell batch under test.
2. Bench validation experiments are executed on the physical test bench using a calibrated digital multimeter, programmable power supply, and contact thermometer.
3. The hardware teammate and software lead review the measured cut-off characteristics and sign off on updated values.
4. The status is transitioned from `PROVISIONAL` to `CONFIRMED`, recording the confirmation date and specific test report reference.
