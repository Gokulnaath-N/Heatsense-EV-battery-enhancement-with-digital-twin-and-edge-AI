import React from "react";
import { Box, Rotate3d, Eye, Flame } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const TwinLabPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-cyan-bright uppercase tracking-wider">
            <span>Explore</span>
            <span className="text-hs-border-primary">/</span>
            <span>Spatial Simulation</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Twin Lab
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Full-resolution interactive 3D digital twin: exploded cell geometry, active jelly roll
            layers, core thermal distribution, and real-time current flow visualization.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Rotate3d className="w-4 h-4 text-hs-cyan-ion" />}
          >
            Reset Orbit Camera
          </Button>
        </div>
      </div>

      {/* Spatial Telemetry Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Core-to-Surface ΔT"
          value={3.42}
          precision={2}
          unit="°C"
          ontology="ESTIMATED"
          sourceNote="Thermal Conduction Model"
          highlight="amber"
        />
        <MetricPrimitive
          label="Jelly Roll Expansion"
          value={0.048}
          precision={3}
          unit="mm"
          ontology="ESTIMATED"
          sourceNote="Thermo-mechanical Proxy"
          highlight="cyan"
        />
        <MetricPrimitive
          label="Surface Temp (T_surf)"
          value={24.98}
          precision={2}
          unit="°C"
          ontology="MEASURED"
          sourceNote="DS18B20 1-Wire Channel"
          highlight="amber"
        />
        <MetricPrimitive
          label="Cylindrical Form Factor"
          value="18650"
          ontology="METADATA"
          sourceNote="18 mm Dia x 65 mm H"
          highlight="none"
        />
      </div>

      {/* 3D Viewport Placeholder Container */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[480px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        {/* Viewport Header Controls */}
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Box className="w-4 h-4 text-hs-cyan-ion" />
            <span className="text-xs font-mono font-semibold text-hs-cyan-bright tracking-wider uppercase">
              WebGL 3D Scene Viewport
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 02 CANVAS READY
          </span>
        </div>

        {/* Center Canvas Callout */}
        <div className="relative z-10 my-auto py-12 flex flex-col items-center justify-center text-center max-w-md mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-cyan-ion/40 flex items-center justify-center shadow-[0_0_30px_rgba(99,221,242,0.15)] mb-4">
            <Box className="w-8 h-8 text-hs-cyan-bright animate-bounce" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Spatial 3D Digital Twin Canvas
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 02 renders the complete procedural 18650 cell: steel can, gasket, current interrupt
            device (CID), positive cap, and unwrapped jelly roll layers with real-time shader heatmaps.
          </p>

          <div className="flex items-center gap-3 mt-6">
            <Button variant="secondary" size="sm" leftIcon={<Eye className="w-3.5 h-3.5" />}>
              Exploded View Toggle
            </Button>
            <Button variant="secondary" size="sm" leftIcon={<Flame className="w-3.5 h-3.5 text-hs-amber-thermal" />}>
              Thermal Shader
            </Button>
          </div>
        </div>

        {/* Viewport Footer */}
        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Camera: Orbital [R: 120mm, Az: 45°, El: 30°]</span>
          <span>Target: Li-ion 18650 (LCO / LFP Profile)</span>
        </div>
      </div>
    </div>
  );
};
