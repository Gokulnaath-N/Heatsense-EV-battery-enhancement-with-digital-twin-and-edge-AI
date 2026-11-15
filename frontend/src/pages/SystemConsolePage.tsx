import React from "react";
import { Terminal, ShieldCheck } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const SystemConsolePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-mint-signal uppercase tracking-wider">
            <span>Operations</span>
            <span className="text-hs-border-primary">/</span>
            <span>Safety &amp; Architecture Audit</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            System Console
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Firmware relay safety isolation monitor, ESP32-WROOM-32 hardware heartbeat, host AST
            architecture guard verification, and Clean / Hexagonal boundary audit.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="relay-closed" />
          <Button variant="outline" size="sm" leftIcon={<Terminal className="w-4 h-4 text-hs-mint-signal" />}>
            Run AST Guard Audit
          </Button>
        </div>
      </div>

      {/* Safety & Architecture Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Firmware Relay Authority"
          value="ENFORCED"
          ontology="MEASURED"
          sourceNote="Host is strictly Advisory"
          highlight="mint"
        />
        <MetricPrimitive
          label="AST Architecture Guard"
          value="0 VIOLATIONS"
          ontology="METADATA"
          sourceNote="Hexagonal Direction Inward"
          highlight="mint"
        />
        <MetricPrimitive
          label="Hardware Heartbeat"
          value="SIMULATED"
          ontology="METADATA"
          sourceNote="Hardware Independence Active"
          highlight="blue"
        />
        <MetricPrimitive
          label="Unit Tests Passing"
          value="42 / 42"
          ontology="METADATA"
          sourceNote="100% Coverage on Domain"
          highlight="mint"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-hs-mint-signal" />
            <span className="text-xs font-mono font-semibold text-hs-mint-signal tracking-wider uppercase">
              Firmware Safety Boundary &amp; AST Guard Console
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 10 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-mint-signal/40 flex items-center justify-center shadow-[0_0_25px_rgba(131,217,178,0.15)] mb-4">
            <ShieldCheck className="w-8 h-8 text-hs-mint-signal" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            Safety Boundary &amp; Architecture Auditor
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 10 renders live AST architecture verification trees, serial wire frame diagnostic
            packet inspections, and real-time validation that no host algorithm has relay trip override authority.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-mint-signal">
              Firmware Sole Tripping Authority: Locked
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-text-secondary">
              Zero Circular Dependencies
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-hs-void border border-hs-border-subtle text-hs-cyan-bright">
              No Direct DB / Serial in Domain
            </span>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Architecture: Clean Hexagonal (Ports &amp; Adapters)</span>
          <span>Safety Standard: Hardware Relay Cutoff Isolated in ESP32 Firmware</span>
        </div>
      </div>
    </div>
  );
};
