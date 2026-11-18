import React from "react";
import { ShieldAlert, AlertTriangle } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const AnomalyObservatoryPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-coral-alert uppercase tracking-wider">
            <span>Intelligence</span>
            <span className="text-hs-border-primary">/</span>
            <span>Precursor Diagnostics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Anomaly Observatory
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Dual-channel cumulative sum (CUSUM) precursor detection, electrical impedance drift,
            thermal precursor isolation, and advisory fault classification.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="coral" size="sm" leftIcon={<AlertTriangle className="w-4 h-4 text-hs-coral-alert" />}>
            Inject Software Fault
          </Button>
        </div>
      </div>

      {/* CUSUM Diagnostic Telemetry */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Electrical CUSUM Score (S_k^elec)"
          value={4.28}
          precision={2}
          ontology="ADVISORY"
          sourceNote="Alarm Threshold = 8.0"
          highlight="mint"
        />
        <MetricPrimitive
          label="Thermal CUSUM Score (S_k^therm)"
          value={0.0}
          precision={2}
          ontology="ADVISORY"
          sourceNote="Alarm Threshold = 8.0"
          highlight="mint"
        />
        <MetricPrimitive
          label="Active Advisory Status"
          value="NORMAL"
          ontology="ADVISORY"
          sourceNote="No configured threshold violated"
          highlight="mint"
        />
        <MetricPrimitive
          label="False Alarm Count"
          value={0}
          ontology="ADVISORY"
          sourceNote="Verified on NASA Baseline"
          highlight="none"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-hs-coral-alert" />
            <span className="text-xs font-mono font-semibold text-hs-coral-alert tracking-wider uppercase">
              Dual-Channel CUSUM Precursor Matrix
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 05 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-coral-alert/40 flex items-center justify-center shadow-[0_0_25px_rgba(255,100,124,0.15)] mb-4">
            <ShieldAlert className="w-8 h-8 text-hs-coral-alert" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Thermal &amp; Impedance Precursor Studio
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 05 delivers dual-channel CUSUM response charts, 5-scenario software fault injection
            matrix (impedance surge, voltage bias, current scale, thermal spike, ADC noise), and latency tracking.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-text-secondary">
              Drift k_elec = 0.50 σ
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-text-secondary">
              Drift k_therm = 0.50 σ
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-coral-alert">
              Host Advisory Only (Non-Tripping)
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Diagnostic Mode: Precursor Anomaly Detection (Statistical Process Control)</span>
          <span>Safety Boundary: Only Firmware Can Open Relay</span>
        </div>
      </div>
    </div>
  );
};
