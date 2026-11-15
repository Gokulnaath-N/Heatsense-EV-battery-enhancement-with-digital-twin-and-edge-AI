import React from "react";
import { FlaskConical, Play, RotateCcw, FastForward } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const ExperimentStudioPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-amber-thermal uppercase tracking-wider">
            <span>Experiments</span>
            <span className="text-hs-border-primary">/</span>
            <span>NASA Replay &amp; Fault Injection</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Experiment Studio
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Deterministic laboratory harness: stream 10 Hz telemetry from NASA battery aging cycles
            (B0005, B0006, B0018), inject synthetic anomalies, and benchmark real-time observer tracking.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="replay" />
          <Button variant="primary" size="sm" leftIcon={<Play className="w-4 h-4" />}>
            Start Replay Stream
          </Button>
        </div>
      </div>

      {/* Replay Status Telemetry */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Active Replay Cell"
          value="NASA B0005"
          ontology="METADATA"
          sourceNote="Cycle 001 (05122.csv)"
          highlight="amber"
        />
        <MetricPrimitive
          label="Playback Speed"
          value="1.0x"
          ontology="METADATA"
          sourceNote="Real-time 10 Hz Sample Clock"
          highlight="none"
        />
        <MetricPrimitive
          label="Replay Frame Index"
          value="142 / 3120"
          ontology="METADATA"
          sourceNote="Elapsed: 00:14:12"
          highlight="cyan"
        />
        <MetricPrimitive
          label="Software Fault State"
          value="CLEAN"
          ontology="ADVISORY"
          sourceNote="No injection active"
          highlight="mint"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-hs-amber-thermal" />
            <span className="text-xs font-mono font-semibold text-hs-amber-thermal tracking-wider uppercase">
              Telemetry Replay &amp; Injection Matrix
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 07 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-amber-thermal/40 flex items-center justify-center shadow-[0_0_25px_rgba(255,182,92,0.15)] mb-4">
            <FlaskConical className="w-8 h-8 text-hs-amber-thermal" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Interactive Playback &amp; Injection Console
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 07 provides scrubbing timeline controls (Play, Pause, Step, Scrub, 1x-10x Speed),
            cell and cycle selector dropdowns, and one-click injection of the 5 audit fault scenarios.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <Button variant="secondary" size="sm" leftIcon={<RotateCcw className="w-3.5 h-3.5" />}>
              Rewind to Cycle Start
            </Button>
            <Button variant="secondary" size="sm" leftIcon={<FastForward className="w-3.5 h-3.5" />}>
              Fast Forward 5x
            </Button>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Replay Adapter: host.infrastructure.adapters.nasa_replay</span>
          <span>Source: NASA Ames Prognostics Data Repository</span>
        </div>
      </div>
    </div>
  );
};
