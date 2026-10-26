# CRC-16/CCITT-FALSE Technical Reference

## 1. Specification Parameters

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Name** | CRC-16/CCITT-FALSE | Canonical Kermit / CCITT-FALSE variant |
| **Polynomial** | `0x1021` | $x^{16} + x^{12} + x^5 + 1$ |
| **Initial Value** | `0xFFFF` | Non-zero seed prevents undetected leading zeros |
| **Reflect In** | `False` | MSB-first bit order |
| **Reflect Out** | `False` | MSB-first bit order |
| **XOR Out** | `0x0000` | No final XOR |
| **Check Vector** | `0x29B1` | CRC over ASCII bytes `"123456789"` |

---

## 2. Mathematical Definition

For byte sequence $B = [b_0, b_1, \dots, b_{n-1}]$, the CRC register $R$ starts at $R_0 = \text{0xFFFF}$.
For each byte $b_k$, the register is updated:

$$R \leftarrow R \oplus (b_k \ll 8)$$

Then, for each of the 8 bits:
$$\text{If } R \ \& \ \text{0x8000} \ne 0 \implies R \leftarrow ((R \ll 1) \oplus \text{0x1021}) \ \& \ \text{0xFFFF}$$
$$\text{Else} \implies R \leftarrow (R \ll 1) \ \& \ \text{0xFFFF}$$

---

## 3. Reference Test Vectors

- `""` (empty) $\to$ `0xFFFF`
- `"A"` $\to$ `0xB915`
- `"123456789"` $\to$ `0x29B1`
- `"HS1,1,100,3800,0,240,241,239,1,0"` $\to$ Calculated and verified in golden test suite.
