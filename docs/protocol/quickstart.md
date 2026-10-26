# HeatSense Protocol v1 Quickstart

## 1. Decoding Frames via CLI

You can decode raw serial frames directly from a file or stdin using `heatsense-decode`:

```bash
# Decode from an ascii wire frame file
heatsense-decode contracts/golden/frames.txt --summary

# Pipe raw bytes via stdin
echo -n '$HS1,1,100,3800,500,245,248,251,2,0*E6E4\r\n' | heatsense-decode -
```

---

## 2. Parsing in Python

```python
from heatsense.domain.services.frame_codec import parse_frame
from heatsense.domain.value_objects.frames import HS1Frame

raw_wire = b"$HS1,1,100,3800,500,245,248,251,2,0*E6E4\r\n"
result = parse_frame(raw_wire)

if result.is_ok():
    frame = result.unwrap()
    if isinstance(frame, HS1Frame):
        print(f"Sample at {frame.t_ms} ms: {frame.v_mv} mV, {frame.i_ma} mA")
else:
    print(f"Decode error: {result.unwrap_err()}")
```
