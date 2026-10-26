# HeatSense Protocol v1 Framing Matrix

| Frame | Verb | Direction | Frequency | Payload Fields | Max Wire Bytes | CRC Scope |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HS1** | Periodic Sample | Device $\to$ Host | 10 Hz (nominal) | 9 fields (seq, t_ms, v_mv, i_ma, t1_dc, t2_dc, t3_dc, state, faults) | 84 B | `$HS1,...*` (excluding `$` and `*`) |
| **HE1** | Hardware Event | Device $\to$ Host | Asynchronous on state/fault | 4 fields (seq, t_ms, event, detail) | 48 B | `$HE1,...*` |
| **HI1** | Device Info | Device $\to$ Host | At boot & on query | 7 fields (fw, ovp_mv, uvp_mv, otp_dc, ocp_ma, rate_hz, test_limits) | 72 B | `$HI1,...*` |
| **HA1** | Command Ack | Device $\to$ Host | Upon host HC1 command | 2 fields (cmd_seq, status) | 32 B | `$HA1,...*` |
| **HC1** | Host Command | Host $\to$ Device | Advisory host commands | 3 fields (seq, cmd, arg) | 48 B | `$HC1,...*` |
