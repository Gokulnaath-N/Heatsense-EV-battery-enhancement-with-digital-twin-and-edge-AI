# HeatSense frontend

Primary UI: React + TypeScript + Vite.

Suggested feature-oriented layout:
- `src/app/`: application composition, router, providers.
- `src/pages/`: route-level screens.
- `src/features/`: datasets, dashboard, Digital Twin, diagnostics, ML workbench, experiments.
- `src/components/`: reusable design-system components.
- `src/lib/api/`: typed API client and endpoint functions.
- `src/types/`: API-aligned types.
- `src/hooks/`: reusable UI hooks.
- `src/styles/`: tokens and global styles.

The frontend must display dataset playback/offline simulation clearly and must not invent live hardware values.
