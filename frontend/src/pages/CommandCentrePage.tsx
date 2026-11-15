import React from "react";
import { Cpu, ShieldCheck, PlayCircle, Layers } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const CommandCentrePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-cyan-bright uppercase tracking-wider">
            <span>Explore</span>
            <span className="text-hs-border-primary">/</span>
            <span>Mission Control</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Command Centre
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Primary operations hub: 18650 cell digital twin preview, real-time physics telemetry
            stream, and firmware relay safety monitoring.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" pulse />
          <Button
            variant="primary"
            size="sm"
            leftIcon={<PlayCircle className="w-4 h-4" />}
            onClick={() => window.location.href = "#/experiment-studio"}
          >
            Launch Replay
          </Button>
        </div>
      </div>

      {/* Primary Key Telemetry Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Terminal Voltage"
          value={3.842}
          precision={3}
          unit="V"
          ontology="MEASURED"
          sourceNote="INA219 Wire (10 Hz)"
          trend={{ direction: "down", delta: "-0.012 V" }}
          highlight="cyan"
        />
        <MetricPrimitive
          label="Discharge Current"
          value={1.002}
          precision={3}
          unit="A"
          ontology="MEASURED"
          sourceNote="I > 0 Convention"
          trend={{ direction: "neutral", delta: "±0.005 A" }}
          highlight="cyan"
        />
        <MetricPrimitive
          label="Estimated Core Temp"
          value={28.4}
          precision={1}
          unit="°C"
          ontology="ESTIMATED"
          sourceNote="Two-Node Observer"
          trend={{ direction: "up", delta: "+0.8 °C" }}
          highlight="amber"
        />
        <MetricPrimitive
          label="Estimated SoC"
          value={76.4}
          precision={1}
          unit="%"
          ontology="ESTIMATED"
          sourceNote="2RC EKF Coulomb Count"
          trend={{ direction: "down", delta: "-1.2%" }}
          highlight="mint"
        />
      </div>

      {/* Main Viewport Shell Placeholder (Ready for Prompt 01) */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[420px] flex flex-col justify-between overflow-hidden shadow-2xl">
        {/* Subtle engineering grid background texture */}
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        {/* Corner alignment crosshairs */}
        <div className="absolute top-3 left-3 font-mono text-[9px] text-hs-text-muted/40 pointer-events-none select-none">
          + HS.CMD.001
        </div>
        <div className="absolute top-3 right-3 font-mono text-[9px] text-hs-text-muted/40 pointer-events-none select-none">
          LATENCY &lt; 20ms +
        </div>
        <div className="absolute bottom-3 left-3 font-mono text-[9px] text-hs-text-muted/40 pointer-events-none select-none">
          + NASA CELL B0005
        </div>
        <div className="absolute bottom-3 right-3 font-mono text-[9px] text-hs-text-muted/40 pointer-events-none select-none">
          FW RELAY: CLOSED +
        </div>

        {/* Viewport Header Status */}
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-hs-cyan-ion shadow-[0_0_8px_rgba(99,221,242,0.8)]" />
            <span className="text-xs font-mono font-semibold text-hs-cyan-bright tracking-wider uppercase">
              3D Twin Spatial Canvas &amp; Mission Viewport
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 01 FOUNDATION READY
          </span>
        </div>

        {/* Center Blueprint Content */}
        <div className="relative z-10 my-auto py-12 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-border-subtle flex items-center justify-center shadow-[0_0_30px_rgba(99,221,242,0.12)] mb-4">
            <Layers className="w-8 h-8 text-hs-cyan-ion" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Mission Operations Viewport
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            In Prompt 01, this viewport houses the live Three.js 3D cylindrical 18650 cell, real-time
            uPlot electrical/thermal synchronized waveforms, and active telemetry ticker.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-2 mt-6">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-hs-elevated border border-hs-border-primary text-hs-text-secondary">
              ✓ Token System Wired
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-hs-elevated border border-hs-border-primary text-hs-text-secondary">
              ✓ Responsive MegaNav Active
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded-full bg-hs-elevated border border-hs-border-primary text-hs-text-secondary">
              ✓ Firmware Relay Advisory Isolated
            </span>
          </div>
        </div>

        {/* Viewport Footer Status Bar */}
        <div className="relative z-10 flex flex-col sm:flex-row items-center justify-between gap-2 pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-hs-text-secondary">
              <Cpu className="w-3.5 h-3.5 text-hs-cyan-ion" />
              <span>Host Backend: http://127.0.0.1:8000</span>
            </span>
            <span className="text-hs-border-primary">|</span>
            <span className="text-hs-text-muted">FastAPI + WebSocket Replay</span>
          </div>
          <div className="flex items-center gap-2 text-hs-mint-signal">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Firmware Relay: Sole Hardware Safety Authority</span>
          </div>
        </div>
      </div>
    </div>
  );
};
