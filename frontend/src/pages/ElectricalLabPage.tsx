import React from "react";
import { Zap, Activity, Sliders } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const ElectricalLabPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-cyan-bright uppercase tracking-wider">
            <span>Intelligence</span>
            <span className="text-hs-border-primary">/</span>
            <span>Physics State Estimation</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Electrical Lab
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Second-Order RC Thévenin equivalent circuit model (2RC ECM) analysis, terminal voltage
            prediction residual, and Innovation-Gated Extended Kalman Filter (EKF) tracking.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="outline" size="sm" leftIcon={<Sliders className="w-4 h-4 text-hs-cyan-ion" />}>
            Adjust Filter Covariance
          </Button>
        </div>
      </div>

      {/* Electrical Observer Telemetry */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Estimated OCV (v_ocv)"
          value={3.891}
          precision={3}
          unit="V"
          ontology="ESTIMATED"
          sourceNote="Polynomial OCV(SoC) Map"
          highlight="cyan"
        />
        <MetricPrimitive
          label="Internal Resistance (R0)"
          value={58.4}
          precision={1}
          unit="mΩ"
          ontology="ESTIMATED"
          sourceNote="ECM Ohmic Impedance"
          highlight="cyan"
        />
        <MetricPrimitive
          label="Terminal Voltage Residual"
          value={4.2}
          precision={1}
          unit="mV"
          ontology="ADVISORY"
          sourceNote="v_measured - v_pred"
          highlight="mint"
        />
        <MetricPrimitive
          label="EKF Innovation Gate"
          value="GATED PASS"
          ontology="ADVISORY"
          sourceNote="Chi-square Threshold = 9.21"
          highlight="mint"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-hs-cyan-ion" />
            <span className="text-xs font-mono font-semibold text-hs-cyan-bright tracking-wider uppercase">
              2RC Equivalent Circuit Model &amp; Innovation Viewport
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 03 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-border-primary flex items-center justify-center shadow-lg mb-4">
            <Activity className="w-8 h-8 text-hs-cyan-ion" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            High-Speed Waveform Studio
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 03 embeds synchronized uPlot high-frequency voltage traces, RC polarization
            overvoltages ($V_1$, $V_2$), and live Chi-square normalized innovation squared (NIS) plots.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-cyan-bright">
              R0 = 58.4 mΩ
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-cyan-bright">
              R1 = 28.1 mΩ, C1 = 1250 F
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-cyan-bright">
              R2 = 42.6 mΩ, C2 = 4800 F
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Filter: 2RC Innovation-Gated EKF (10 Hz Execution Rate)</span>
          <span>Sign Convention: I &gt; 0 = Discharge</span>
        </div>
      </div>
    </div>
  );
};
