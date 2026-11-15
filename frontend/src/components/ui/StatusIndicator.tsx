import React from "react";
import { CheckCircle2, AlertTriangle, Radio, WifiOff, Disc, ShieldAlert } from "lucide-react";

export type StatusType =
  | "normal"
  | "advisory-alert"
  | "online"
  | "offline"
  | "replay"
  | "relay-closed"
  | "relay-tripped";

export interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  size?: "sm" | "md";
  pulse?: boolean;
  className?: string;
  showIcon?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = "md",
  pulse = false,
  className = "",
  showIcon = true,
}) => {
  const configs: Record<
    StatusType,
    {
      dotClass: string;
      bgClass: string;
      textClass: string;
      borderClass: string;
      defaultLabel: string;
      icon: React.ReactNode;
    }
  > = {
    normal: {
      dotClass: "bg-hs-mint-signal shadow-[0_0_8px_rgba(131,217,178,0.6)]",
      bgClass: "bg-hs-mint-signal/10",
      textClass: "text-hs-mint-signal",
      borderClass: "border-hs-mint-signal/30",
      defaultLabel: "NORMAL (NO THRESHOLD VIOLATION)",
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-hs-mint-signal shrink-0" />,
    },
    "advisory-alert": {
      dotClass: "bg-hs-coral-alert shadow-[0_0_8px_rgba(255,100,124,0.7)] animate-pulse",
      bgClass: "bg-hs-coral-alert/15",
      textClass: "text-hs-coral-alert",
      borderClass: "border-hs-coral-alert/40",
      defaultLabel: "ADVISORY ALARM (HOST ONLY)",
      icon: <AlertTriangle className="w-3.5 h-3.5 text-hs-coral-alert shrink-0" />,
    },
    online: {
      dotClass: "bg-hs-cyan-ion shadow-[0_0_8px_rgba(99,221,242,0.6)]",
      bgClass: "bg-hs-cyan-deep/20",
      textClass: "text-hs-cyan-bright",
      borderClass: "border-hs-cyan-ion/30",
      defaultLabel: "HOST BACKEND ONLINE",
      icon: <Radio className="w-3.5 h-3.5 text-hs-cyan-bright shrink-0" />,
    },
    offline: {
      dotClass: "bg-hs-text-muted shadow-none",
      bgClass: "bg-hs-elevated",
      textClass: "text-hs-text-muted",
      borderClass: "border-hs-border-primary",
      defaultLabel: "DISCONNECTED",
      icon: <WifiOff className="w-3.5 h-3.5 text-hs-text-muted shrink-0" />,
    },
    replay: {
      dotClass: "bg-hs-amber-thermal shadow-[0_0_8px_rgba(255,182,92,0.6)]",
      bgClass: "bg-hs-amber-thermal/10",
      textClass: "text-hs-amber-thermal",
      borderClass: "border-hs-amber-thermal/30",
      defaultLabel: "TELEMETRY REPLAY",
      icon: <Disc className="w-3.5 h-3.5 text-hs-amber-thermal shrink-0 animate-spin" />,
    },
    "relay-closed": {
      dotClass: "bg-hs-mint-signal shadow-[0_0_8px_rgba(131,217,178,0.6)]",
      bgClass: "bg-hs-mint-signal/10",
      textClass: "text-hs-mint-signal",
      borderClass: "border-hs-mint-signal/30",
      defaultLabel: "FW RELAY ENGAGED (CLOSED)",
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-hs-mint-signal shrink-0" />,
    },
    "relay-tripped": {
      dotClass: "bg-hs-coral-alert shadow-[0_0_10px_rgba(255,100,124,0.8)]",
      bgClass: "bg-hs-coral-alert/20",
      textClass: "text-hs-coral-alert",
      borderClass: "border-hs-coral-alert/50",
      defaultLabel: "FW RELAY TRIPPED (OPEN)",
      icon: <ShieldAlert className="w-3.5 h-3.5 text-hs-coral-alert shrink-0" />,
    },
  };

  const current = configs[status];
  const displayLabel = label ?? current.defaultLabel;

  const sizeClasses =
    size === "sm"
      ? "text-[10px] px-2 py-0.5 gap-1.5 font-medium"
      : "text-xs px-2.5 py-1 gap-2 font-semibold";

  return (
    <div
      className={`inline-flex items-center rounded-full border ${current.bgClass} ${current.borderClass} ${sizeClasses} select-none ${className}`}
      title={displayLabel}
    >
      <span className="relative flex h-2 w-2 shrink-0">
        {pulse && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${current.dotClass}`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${current.dotClass}`} />
      </span>

      {showIcon && current.icon}

      <span className={`tracking-wider uppercase font-mono ${current.textClass}`}>
        {displayLabel}
      </span>
    </div>
  );
};

