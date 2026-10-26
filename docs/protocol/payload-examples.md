# HeatSense Protocol v1 Payload Examples

This document lists canonical ASCII wire representations for each supported frame type.

---

## 1. Periodic Telemetry (HS1)

### Nominal Sample
```text
$HS1,1,100,4150,420,245,248,242,2,0*BB31\r\n
```
- Sequence: `1`
- Microcontroller Time: `100` ms
- Voltage: `4150` mV ($4.150\text{ V}$)
- Current: `420` mA ($0.420\text{ A}$ discharge)
- Temperatures: `245`, `248`, `242` ($24.5^\circ\text{C}$, $24.8^\circ\text{C}$, $24.2^\circ\text{C}$)
- Device State: `2` (`ARMED_CLOSED`)
- Fault Bitmask: `0` (`NONE`)
- Checksum: `0xBB31`

---

## 2. Hardware Event (HE1)

### Armed Confirmation
```text
$HE1,1,100,1,0*1B5B\r\n
```
- Sequence: `1`
- Event: `1` (`ARM_OK`)
- Detail: `0`

---

## 3. Device Handshake & Limits (HI1)

```text
$HI1,v1.0.0,4250,2800,450,2000,10,0*C75B\r\n
```
- Firmware Version: `v1.0.0`
- OVP Limit: `4250` mV
- UVP Limit: `2800` mV
- OTP Limit: `450` ($45.0^\circ\text{C}$)
- OCP Limit: `2000` mA
- Telemetry Rate: `10` Hz
- Test Limits Flag: `0` (Production safety limits active)

---

## 4. Command Acknowledgement (HA1)

### Command Accepted
```text
$HA1,1,0*C9B1\r\n
```
- Acknowledged Sequence: `1`
- Status: `0` (`OK`)

---

## 5. Host Command (HC1)

### Advisory Ping Command
```text
$HC1,1,PING,0*7B3D\r\n
```
- Host Sequence: `1`
- Command: `PING`
- Argument: `0`
