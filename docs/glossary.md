# HeatSense Glossary

This glossary establishes canonical definitions, measurement conventions, and unit standards across all HeatSense software and documentation.

---

## Sign Convention and Units

HeatSense strictly enforces consistent electrical and thermal units. Conversions occur solely at boundary adapters.

| Quantity | Wire / Serialization Unit | Domain Unit (SI) | Convention / Notes |
| :--- | :--- | :--- | :--- |
| Current ($I$) | Milliamperes (`mA`) | Amperes (`A`) | **$I > 0$ denotes DISCHARGE**. Current flowing out of the cell into the load is positive. Charging current is negative ($I < 0$). |
| Voltage ($V$) | Millivolts (`mV`) | Volts (`V`) | Cell terminal potential difference. |
| Surface Temperature ($T_{\text{surface}}$) | Deci-Celsius ($0.1\,^{\circ}\text{C}$) | Degrees Celsius ($^{\circ}\text{C}$) | Integer representation on wire ($254 = 25.4\,^{\circ}\text{C}$). |
| Core Temperature ($T_{\text{core}}$) | N/A (Internal only) | Degrees Celsius ($^{\circ}\text{C}$) | Estimated state variable; never measured directly. |
| Resistance ($R$) | Milliohms ($m\Omega$) | Ohms ($\Omega$) | Ohmic series resistance $R_s$ and RC branch resistances. |
| Capacitance ($C$) | Millifarads ($mF$) / Farads ($F$) | Farads ($F$) | Equivalent-circuit diffusion branch capacitances. |
| Device Time | Milliseconds (`ms`) | Seconds ($s$) | Microcontroller `uint32` millisecond counter; wraps at ~49.7 days. |
| Host Time | Milliseconds (`ms`) | Seconds ($s$) | POSIX timestamp since epoch acquired via `Clock` port. |

---

## Domain Terminology

### SoC (estimated)
- **Definition**: State of Charge. The ratio of currently available electrical charge to nominal cell capacity, expressed as a fraction ($0.0 \le \text{SoC} \le 1.0$) or percentage.
- **Unit**: Dimensionless float ($0.0$ to $1.0$).
- **Distinction**: Must always be referred to as "estimated SoC", as internal charge cannot be measured directly during cell operation.

### SoH proxy
- **Definition**: State of Health proxy. A relative indicator of degradation tracking capacity loss or internal resistance growth relative to initial nominal values.
- **Unit**: Dimensionless ratio ($0.0$ to $1.0$).
- **Distinction**: Must never be referred to as a direct measurement. It is an inferred metric derived from parameter tracking over multiple cycles.

### RUL (not validated)
- **Definition**: Remaining Useful Life. An estimated projection of remaining operating cycles or duration before the cell reaches end-of-life criteria (e.g., 80% nominal capacity retention).
- **Unit**: Cycles or operating hours.
- **Distinction**: Must always be qualified as "RUL (not validated)" because long-term prognostic aging models have not been validated against experimental multi-month cell datasets.

### OCV
- **Definition**: Open Circuit Voltage. The thermodynamic terminal equilibrium voltage of the cell when zero current flows and all internal polarization dynamics have fully decayed.
- **Unit**: Volts ($V$).
- **Distinction**: Mapped non-linearly to SoC via an empirical OCV-SoC lookup table or polynomial function.

### 2RC ECM
- **Definition**: Second-Order Resistor-Capacitor Equivalent Circuit Model. A lumped-parameter electrical model representing the cell as an open-circuit voltage source in series with an ohmic resistance ($R_s$) and two parallel resistor-capacitor pairs ($R_1 \parallel C_1$ for fast charge-transfer kinetics, $R_2 \parallel C_2$ for slow mass-transport diffusion dynamics).
- **Unit**: Voltages ($V$), resistances ($\Omega$), capacitances ($F$).

### EKF
- **Definition**: Extended Kalman Filter. A non-linear recursive Bayesian state estimation algorithm that estimates hidden state variables (such as SoC and polarization voltages) by fusing physical 2RC model predictions with real-time terminal voltage and current measurements under Gaussian noise assumptions.

### Innovation
- **Definition**: Measurement pre-fit residual in the Kalman filter. The difference between the actual observed terminal voltage and the voltage predicted by the model prior to state correction: $y_k = z_k - h(\hat{x}_k^-)$.
- **Unit**: Volts ($V$).

### NIS
- **Definition**: Normalized Innovation Squared. A statistical metric calculated as $\epsilon_k = y_k^T S_k^{-1} y_k$ (where $S_k$ is the innovation covariance). Used to evaluate Kalman filter consistency and detect model mismatch or sensor degradation.
- **Unit**: Dimensionless scalar.

### T_core (estimated, uncalibrated)
- **Definition**: Estimated lumped internal core temperature of the cylindrical 18650 cell, calculated via a two-node (core-surface) thermal model driven by Joule heating ($I^2 R$) and convective heat dissipation.
- **Unit**: Degrees Celsius ($^{\circ}\text{C}$).
- **Distinction**: Must always be qualified as "estimated, uncalibrated" because physical core temperature is not directly accessible without destructive cell penetration.

### T_surface
- **Definition**: Physical surface temperature measured by digital DS18B20 temperature probes mounted on the exterior can of the cell.
- **Unit**: Degrees Celsius ($^{\circ}\text{C}$).

### R_s
- **Definition**: Series ohmic resistance. The immediate instantaneous resistance of the cell electrolyte, current collectors, and tabs, manifested as an abrupt voltage drop or jump upon current interruption.
- **Unit**: Ohms ($\Omega$) or Milliohms ($m\Omega$).

### Polarization Voltage
- **Definition**: The transient overpotential across the RC branches ($U_1$ and $U_2$) resulting from electrochemical charge-transfer resistance and solid-state lithium-ion diffusion gradients.
- **Unit**: Volts ($V$).

### Telemetry Frame
- **Definition**: A binary serialized data packet structured according to the protocol specification, transmitted periodically from the ESP32 firmware over USB serial to the host, containing voltage, current, temperatures, relay status, and CRC error-detection bytes.

### Golden Frame
- **Definition**: A curated, immutable binary telemetry frame stored in `contracts/golden/`, accompanied by known-valid decoded ground truth fields. Used by both firmware and host test runners to verify byte-exact decoder compatibility.

### Port
- **Definition**: An abstract structural interface (defined using Python `typing.Protocol` or `abc.ABC`) in the domain layer that specifies an external capability (such as I/O, persistence, or timing) required by domain and application logic.

### Adapter
- **Definition**: A concrete infrastructure class that implements a domain port by wrapping third-party libraries, operating system features, or physical hardware (e.g., `SerialTransport`, `SqliteSampleRepository`).

### Composition Root
- **Definition**: The centralized location in the application (`heatsense/bootstrap.py`) where concrete adapters are instantiated and injected into application services and domain ports.

### Advisory Layer
- **Definition**: The host software, estimators, and anomaly detection algorithms whose outputs are strictly informational and non-authoritative. The advisory layer may generate operator warnings and request actions, but can never command safety trips or override firmware protection.

### Latched Fault
- **Definition**: An error condition in the firmware where a hard safety limit was exceeded, causing immediate relay opening. The firmware remains latched in a faulted state until an explicit, human-authorized reset sequence is received after operating conditions return to normal.

### ARM / DISARM
- **Definition**: Host-initiated advisory device commands. `DISARM` requests the firmware to open the load relay. `ARM` requests the firmware to close the load relay, subject to strict firmware pre-checks (voltage, current, and temperature within safety boundaries).

### PROVISIONAL
- **Definition**: A status explicitly assigned to physical parameters, safety limits, or model coefficients that are based on engineering estimates, generic datasheets, or uncalibrated bench setups rather than confirmed cell testing. Requires an identified source.

### [not yet measured]
- **Definition**: Mandatory verbatim placeholder assigned to any quantitative benchmark, evaluation metric, accuracy claim, or runtime latency figure that has not yet been experimentally measured and verified.
