# NASA dataset inspection checklist

Dataset root: `HEATSENSE_DATASET_ROOT` pointing to `D:/Professional Projects/Digital_twin_project/Datasets/cleaned_dataset`.

Inspect without modifying source files:

- [ ] List directory tree and file extensions.
- [ ] Inspect `metadata` format and contents.
- [ ] Inspect representative files under `data/` (first, middle, last if feasible).
- [ ] Inspect representative files under `extra_infos/`.
- [ ] Determine whether sequential files represent records, experiments, cells, cycles, or chunks.
- [ ] Determine schema, delimiters, encodings, and data types.
- [ ] Identify time/timestamp representation and sampling intervals.
- [ ] Identify voltage/current/temperature columns and units.
- [ ] Identify charge/discharge sign convention and operating modes.
- [ ] Identify cell identifiers and cycle identifiers.
- [ ] Identify capacity/SoH labels and how they were measured.
- [ ] Check missing values, duplicates, non-monotonic timestamps, and outliers.
- [ ] Record provenance and metadata links.
- [ ] Produce a data dictionary and sample-row report.
- [ ] Decide whether records can safely be concatenated and under what grouping key.

Do not begin a full parser until the above are understood. Do not rename, move, overwrite, or clean the source data in place.
