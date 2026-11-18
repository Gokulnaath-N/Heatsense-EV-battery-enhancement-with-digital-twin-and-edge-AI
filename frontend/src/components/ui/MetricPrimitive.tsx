import React from "react";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

export type MetricOntology = "MEASURED" | "ESTIMATED" | "ADVISORY" | "METADATA";

export interface MetricPrimitiveProps {
  label: string;
  value: string | number;
  unit?: string;
  ontology: MetricOntology;
  sourceNote?: string;
  trend?: {
    direction: "up" | "down" | "neutral";
    delta: string;
  };
  highlight?: "cyan" | "amber" | "coral" | "mint" | "blue" | "none";
  precision?: number;
  className?: string;
  tooltip?: string;
}

export const MetricPrimitive: React.FC<MetricPrimitiveProps> = ({
  label,
  value,
  unit,
  ontology,
  sourceNote,
  trend,
  highlight = "none",
  precision,
  className = "",
  tooltip,
}) => {
  const ontologyStyles: Record<
    MetricOntology,
    { badge: string; text: string; border: string; desc: string }
  > = {
    MEASURED: {
      badge: "bg-hs-cyan-deep/30 text-hs-cyan-bright border-hs-cyan-ion/40",
      text: "text-hs-cyan-bright",
      border: "border-hs-cyan-ion/30",
      desc: "Direct physical sensor telemetry (INA219 / DS18B20)",
    },
    ESTIMATED: {
      badge: "bg-hs-amber-thermal/15 text-hs-amber-thermal border-hs-amber-thermal/40",
      text: "text-hs-amber-thermal",
      border: "border-hs-amber-thermal/30",
      desc: "Physics observer state (2RC EKF / Two-Node Thermal / SoH Proxy)",
    },
    ADVISORY: {
      badge: "bg-hs-coral-alert/15 text-hs-coral-alert border-hs-coral-alert/40",
      text: "text-hs-coral-alert",
      border: "border-hs-coral-alert/30",
      desc: "Advisory diagnostic precursor (Dual CUSUM / Innovation Gate)",
    },
    METADATA: {
      badge: "bg-hs-elevated text-hs-text-muted border-hs-border-primary",
      text: "text-hs-text-muted",
      border: "border-hs-border-subtle",
      desc: "Operational telemetry index / device timestamp",
    },
  };

  const highlightStyles = {
    cyan: "border-l-2 border-l-hs-cyan-ion",
    amber: "border-l-2 border-l-hs-amber-thermal",
    coral: "border-l-2 border-l-hs-coral-alert",
    mint: "border-l-2 border-l-hs-mint-signal",
    blue: "border-l-2 border-l-hs-blue-info",
    none: "",
  };

  const formattedValue =
    typeof value === "number" && precision !== undefined
      ? value.toFixed(precision)
      : value;

  const currentOntology = ontologyStyles[ontology];

  return (
    <div
      className={`relative flex flex-col p-3.5 rounded-xl bg-hs-graphite/75 border border-hs-border-primary/80 backdrop-blur-sm transition-all hover:border-hs-border-subtle ${highlightStyles[highlight]} ${className}`}
      title={tooltip || `${label}: ${formattedValue} ${unit || ""} [${currentOntology.desc}]`}
    >
      {/* Header: Label + Ontological Badge */}
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className="text-[11px] font-medium uppercase tracking-wider text-hs-text-muted truncate">
          {label}
        </span>
        <span
          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono font-semibold tracking-wider border uppercase ${currentOntology.badge}`}
          title={currentOntology.desc}
        >
          {ontology}
        </span>
      </div>

      {/* Main Value + Unit */}
      <div className="flex items-baseline gap-1.5 my-0.5">
        <span className="text-2xl font-mono font-bold tracking-tight text-hs-text-primary tabular-nums">
          {formattedValue}
        </span>
        {unit && (
          <span className="text-xs font-mono text-hs-text-muted uppercase tracking-tight">
            {unit}
          </span>
        )}
      </div>

      {/* Footer: Trend or Source note */}
      <div className="flex items-center justify-between mt-1 text-[11px] text-hs-text-muted/80">
        {sourceNote ? (
          <span className="font-mono text-[10px] text-hs-text-muted/70 truncate">
            {sourceNote}
          </span>
        ) : (
          <span />
        )}

        {trend && (
          <div
            className={`inline-flex items-center gap-0.5 font-mono text-[10px] font-medium ${
              trend.direction === "up"
                ? "text-hs-cyan-bright"
                : trend.direction === "down"
                ? "text-hs-amber-thermal"
                : "text-hs-text-muted"
            }`}
          >
            {trend.direction === "up" && <ArrowUpRight className="w-3 h-3" />}
            {trend.direction === "down" && <ArrowDownRight className="w-3 h-3" />}
            {trend.direction === "neutral" && <Minus className="w-3 h-3" />}
            <span>{trend.delta}</span>
          </div>
        )}
      </div>
    </div>
  );
};
