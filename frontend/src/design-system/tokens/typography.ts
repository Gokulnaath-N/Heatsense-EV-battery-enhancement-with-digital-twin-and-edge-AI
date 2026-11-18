/**
 * HeatSense Typography Tokens
 * Space Grotesk (Display) | Inter (Interface) | JetBrains Mono (Technical Telemetry)
 */

export const typography = {
  families: {
    display: "'Space Grotesk', Sora, sans-serif",
    interface: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
    technical: "'JetBrains Mono', monospace",
  },
  scales: {
    displayXl: {
      fontSize: "clamp(3.5rem, 6vw, 4.75rem)",
      lineHeight: "1.05",
      letterSpacing: "-0.03em",
      fontWeight: "700",
    },
    displayL: {
      fontSize: "clamp(2.5rem, 4.5vw, 3.25rem)",
      lineHeight: "1.1",
      letterSpacing: "-0.025em",
      fontWeight: "700",
    },
    h1: {
      fontSize: "2.25rem",
      lineHeight: "1.2",
      letterSpacing: "-0.02em",
      fontWeight: "600",
    },
    h2: {
      fontSize: "1.875rem",
      lineHeight: "1.25",
      letterSpacing: "-0.015em",
      fontWeight: "600",
    },
    h3: {
      fontSize: "1.5rem",
      lineHeight: "1.3",
      letterSpacing: "-0.01em",
      fontWeight: "600",
    },
    h4: {
      fontSize: "1.25rem",
      lineHeight: "1.35",
      letterSpacing: "-0.005em",
      fontWeight: "600",
    },
    bodyLarge: {
      fontSize: "1.0625rem",
      lineHeight: "1.5",
      fontWeight: "400",
    },
    body: {
      fontSize: "0.9375rem",
      lineHeight: "1.55",
      fontWeight: "400",
    },
    caption: {
      fontSize: "0.8125rem",
      lineHeight: "1.4",
      fontWeight: "400",
    },
    technical: {
      fontSize: "0.6875rem",
      lineHeight: "1.3",
      letterSpacing: "0.08em",
      fontWeight: "500",
      textTransform: "uppercase" as const,
    },
  },
} as const;

export type TypographyTokens = typeof typography;
