import React from "react";
import { History, Clock, Filter } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const EventTimelinePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-blue-info uppercase tracking-wider">
            <span>Operations</span>
            <span className="text-hs-border-primary">/</span>
            <span>Audit &amp; Diagnostics</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Event Timeline
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Cryptographically timestamped, chronological log of system state transitions, CUSUM threshold
            excursions, advisory alerts, and relay state verifications.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="outline" size="sm" leftIcon={<Filter className="w-4 h-4" />}>
            Filter by Severity
          </Button>
        </div>
      </div>

      {/* Timeline Telemetry Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Logged Events (Session)"
          value="18"
          ontology="METADATA"
          sourceNote="Since Session Start"
          highlight="blue"
        />
        <MetricPrimitive
          label="Advisory Warnings"
          value="0"
          ontology="ADVISORY"
          sourceNote="Host-side CUSUM alerts"
          highlight="mint"
        />
        <MetricPrimitive
          label="Firmware Relay Trips"
          value="0"
          ontology="MEASURED"
          sourceNote="Hardware Relay Actuations"
          highlight="mint"
        />
        <MetricPrimitive
          label="Audit Integrity"
          value="VERIFIED"
          ontology="METADATA"
          sourceNote="Sequential monotonically"
          highlight="mint"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-hs-blue-info" />
            <span className="text-xs font-mono font-semibold text-hs-blue-info tracking-wider uppercase">
              Sequential Audit Log &amp; Causality Stream
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 09 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-blue-info/40 flex items-center justify-center shadow-[0_0_25px_rgba(125,175,255,0.15)] mb-4">
            <Clock className="w-8 h-8 text-hs-blue-info" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Causality Inspection Timeline
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 09 features an interactive visual timeline showing exact millisecond causality
            chains: sensor perturbation → EKF innovation spike → CUSUM accumulator trip → Advisory dispatch.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-text-secondary">
              Monotonic Clock: Clock Port (Zero Wallclock Drift)
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-mint-signal">
              Audit Guard: Zero Silent Fallbacks
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Log Engine: host.application.alert_engine</span>
          <span>Time Resolution: 1 ms device timestamp + Host receipt timestamp</span>
        </div>
      </div>
    </div>
  );
};
