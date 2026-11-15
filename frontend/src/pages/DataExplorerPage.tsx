import React from "react";
import { Database, Download, Filter, RefreshCw } from "lucide-react";
import { MetricPrimitive } from "../components/ui/MetricPrimitive";
import { StatusIndicator } from "../components/ui/StatusIndicator";
import { Button } from "../components/ui/Button";

export const DataExplorerPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-hs-border-primary/60">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-xs font-mono text-hs-blue-info uppercase tracking-wider">
            <span>Experiments</span>
            <span className="text-hs-border-primary">/</span>
            <span>Data Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-hs-text-primary tracking-tight">
            Data Explorer
          </h1>
          <p className="text-xs sm:text-sm text-hs-text-secondary max-w-2xl font-sans">
            Multi-dimensional telemetry querying, cross-channel parameter correlation (V vs T vs R_0),
            high-rate sample filtering, and CSV / JSON data export.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <StatusIndicator status="normal" />
          <Button variant="outline" size="sm" leftIcon={<Download className="w-4 h-4 text-hs-blue-info" />}>
            Export Query CSV
          </Button>
        </div>
      </div>

      {/* Explorer Telemetry Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <MetricPrimitive
          label="Total Stored Samples"
          value="48,120"
          ontology="METADATA"
          sourceNote="SQLite Local Repository"
          highlight="blue"
        />
        <MetricPrimitive
          label="Active Filter Window"
          value="Last 30 Min"
          ontology="METADATA"
          sourceNote="18,000 samples @ 10Hz"
          highlight="none"
        />
        <MetricPrimitive
          label="Pearson Correlation (V vs T)"
          value="-0.884"
          precision={3}
          ontology="ESTIMATED"
          sourceNote="Inverted Voltage vs Temp"
          highlight="cyan"
        />
        <MetricPrimitive
          label="Downsample Factor"
          value="1:1 (Raw)"
          ontology="METADATA"
          sourceNote="Full fidelity streaming"
          highlight="none"
        />
      </div>

      {/* Analytical Viewport Shell */}
      <div className="relative rounded-2xl bg-hs-graphite/60 border border-hs-border-primary p-6 sm:p-8 min-h-[440px] flex flex-col justify-between overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-hs-engineering-grid opacity-20 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-hs-blue-info" />
            <span className="text-xs font-mono font-semibold text-hs-blue-info tracking-wider uppercase">
              Cross-Channel Correlation Matrix &amp; Data Grid
            </span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-void border border-hs-border-subtle text-hs-text-muted">
            PROMPT 08 READY
          </span>
        </div>

        <div className="relative z-10 my-auto py-10 flex flex-col items-center justify-center text-center max-w-lg mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-hs-elevated border border-hs-blue-info/40 flex items-center justify-center shadow-[0_0_25px_rgba(125,175,255,0.15)] mb-4">
            <Database className="w-8 h-8 text-hs-blue-info" />
          </div>
          <h2 className="text-lg sm:text-xl font-display font-bold text-hs-text-primary">
            High-Performance Telemetry Table
          </h2>
          <p className="text-xs sm:text-sm text-hs-text-muted mt-2 leading-relaxed">
            Prompt 08 introduces virtualized data tables capable of rendering 100k+ rows at 60fps,
            multi-column scatter plots, and instantaneous CSV export of wire and SI units.
          </p>

          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            <Button variant="secondary" size="sm" leftIcon={<Filter className="w-3.5 h-3.5" />}>
              Configure Channel Filters
            </Button>
            <Button variant="secondary" size="sm" leftIcon={<RefreshCw className="w-3.5 h-3.5" />}>
              Refresh Sample Cache
            </Button>
          </div>
        </div>

        <div className="relative z-10 flex items-center justify-between pt-4 border-t border-hs-border-primary/50 text-xs font-mono text-hs-text-muted">
          <span>Storage Engine: SQLite (host.infrastructure.adapters.sqlite)</span>
          <span>Wire vs Domain: Millivolts (Wire) / Volts (SI Domain)</span>
        </div>
      </div>
    </div>
  );
};
