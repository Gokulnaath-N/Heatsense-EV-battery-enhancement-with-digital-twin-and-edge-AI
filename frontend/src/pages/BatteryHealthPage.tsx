import React from "react";
import { TrendingDown, BarChart3 } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const BatteryHealthPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-mint-signal uppercase tracking-wider">
            <span>Intelligence</span>
            <span className="text-hs-border-primary">/</span>
            <span>Degradation &amp; Lifetime</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Battery Health
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Hybrid Ridge Regression + XGBoost residual SoH proxy estimator, multi-cell Leave-One-Cell-Out
            (LOCO) validation scorecard, capacity fade trajectory, and RUL estimation (not validated).
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="outline" size="sm" leftIcon={<BarChart3 className="w-4 h-4 text-hs-mint-signal" />}>
            Model Comparison
          </Button>
        </div>
      </div>

      {/* Health Telemetry Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Estimated SoH Proxy"
          value={88.4}
          precision={1}
          unit="%"
          ontology="ESTIMATED"
          sourceNote="Hybrid Ridge+XGBoost"
          trend={{ direction: "down", delta: "-0.04%/cyc" }}
          highlight="mint"
        />
        <MetricPrimitive
          label="Discharge Capacity"
          value={1.635}
          precision={3}
          unit="Ah"
          ontology="ESTIMATED"
          sourceNote="Nominal = 2.000 Ah"
          trend={{ direction: "down", delta: "-2.1 mAh" }}
          highlight="mint"
        />
        <MetricPrimitive
          label="LOCO-CV Mean RMSE"
          value={24.3}
          precision={1}
          unit="mAh"
          ontology="ESTIMATED"
          sourceNote="Held-Out NASA B0005/6/18"
          highlight="mint"
        />
        <MetricPrimitive
          label="RUL (Not Validated)"
          value="~42"
          unit="CYC"
          ontology="ADVISORY"
          sourceNote="EOL Threshold = 1.40 Ah"
          highlight="none"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-hs-mint-signal" />
            <span className="text-xs font-mono font-semibold text-hs-mint-signal tracking-wider uppercase">
              Capacity Fade &amp; Hybrid Model Viewport
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 06 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-mint-signal/40 flex items-center justify-center shadow-[0_0_25px_rgba(131,217,178,0.15)] mb-4">
            <TrendingDown className="w-8 h-8 text-hs-mint-signal" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Hybrid Ridge + XGBoost Benchmark Studio
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 06 renders the complete multi-cell capacity degradation curves, extrapolation
            diagnostics on unseen cells (B0006 168-cycle trajectory), and LOCO-CV error distributions.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-mint-signal">
              Hybrid RMSE = 24.3 mAh
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-text-secondary">
              Ridge Alone = 26.2 mAh
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-coral-alert">
              Standalone XGB = 42.3 mAh
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Validation Standard: 3-Cell Leave-One-Cell-Out Cross-Validation</span>
          <span>Terminology: Estimated SoH Proxy (Never Measured SoH)</span>
        </div>
      </div>
    </div>
  );
};
