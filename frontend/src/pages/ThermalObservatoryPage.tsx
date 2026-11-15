import React from "react";
import { Thermometer, Flame } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const ThermalObservatoryPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-amber-thermal uppercase tracking-wider">
            <span>Intelligence</span>
            <span className="text-hs-border-primary">/</span>
            <span>Thermal Dynamics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Thermal Observatory
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Two-Node Thermal Observer tracking internal core temperature ($T_c$), measured surface
            temperature ($T_s$), conduction thermal resistance ($R_c$), and convective heat dissipation ($R_u$).
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="outline" size="sm" leftIcon={<Flame className="w-4 h-4 text-hs-amber-thermal" />}>
            Thermal Runaway Bounds
          </Button>
        </div>
      </div>

      {/* Thermal Telemetry Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Estimated Core Temp (T_c)"
          value={31.2}
          precision={1}
          unit="°C"
          ontology="ESTIMATED"
          sourceNote="Two-Node Observer Model"
          trend={{ direction: "up", delta: "+0.3 °C/min" }}
          highlight="amber"
        />
        <MetricPrimitive
          label="Measured Surface Temp (T_s)"
          value={26.4}
          precision={1}
          unit="°C"
          ontology="MEASURED"
          sourceNote="DS18B20 Contact Probe"
          trend={{ direction: "up", delta: "+0.2 °C/min" }}
          highlight="amber"
        />
        <MetricPrimitive
          label="Joule Heat Generation (Q_gen)"
          value={1.42}
          precision={2}
          unit="W"
          ontology="ESTIMATED"
          sourceNote="I²·R_ohm + Entropic Heat"
          highlight="amber"
        />
        <MetricPrimitive
          label="Core-Surface Gradient (ΔT)"
          value={4.8}
          precision={1}
          unit="°C"
          ontology="ESTIMATED"
          sourceNote="R_c = 1.94 K/W"
          highlight="mint"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Thermometer className="w-4 h-4 text-hs-amber-thermal" />
            <span className="text-xs font-mono font-semibold text-hs-amber-thermal tracking-wider uppercase">
              Two-Node Lumped Parameter Thermal Studio
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 04 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-amber-thermal/40 flex items-center justify-center shadow-[0_0_25px_rgba(255,182,92,0.12)] mb-4">
            <Flame className="w-8 h-8 text-hs-amber-thermal" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Thermal Conduction &amp; Gradient Canvas
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 04 renders radial temperature gradient heatmaps, heat rejection dissipation curves,
            and ambient-compensated continuous thermal state estimation.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-amber-thermal">
              C_c = 62.7 J/K (Core Capacity)
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-amber-thermal">
              C_s = 4.5 J/K (Casing Capacity)
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-amber-thermal">
              R_u = 12.8 K/W (Convective)
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Observer: Two-Node Lumped Thermal ODE (Runge-Kutta 4th Order)</span>
          <span>Honesty Rule: Core Temp is Estimated, Surface Temp is Measured</span>
        </div>
      </div>
    </div>
  );
};
