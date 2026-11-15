/**
 * HeatSense Spacing, Layout & Radius Tokens
 * Based on strict 4-point design grid
 */

export const spacing = {
  grid: {
    1: "4px",
    2: "8px",
    3: "12px",
    4: "16px",
    5: "20px",
    6: "24px",
    8: "32px",
    10: "40px",
    12: "48px",
    16: "64px",
    20: "80px",
    24: "96px",
    32: "128px",
  },
  gutters: {
    desktop: "40px",
    tablet: "24px",
    mobile: "16px",
  },
  radii: {
    control: "8px",
    input: "10px",
    panel: "14px",
    card: "18px",
    megaNav: "20px",
  },
  elevation: {
    base: "0 4px 20px -2px rgba(7, 11, 18, 0.7)",
    raised: "0 8px 30px -4px rgba(7, 11, 18, 0.85)",
    floating: "0 20px 40px -10px rgba(0, 0, 0, 0.9)",
    megaMenu: "0 30px 60px -15px rgba(0, 0, 0, 0.95)",
  },
} as const;

export const radii = spacing.radii;
export const elevations = spacing.elevation;
export type SpacingTokens = typeof spacing;
