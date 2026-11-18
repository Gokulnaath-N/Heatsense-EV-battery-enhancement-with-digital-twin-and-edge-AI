/**
 * HeatSense Global Color Tokens
 * Cryo-Graphite + Ion Cyan + Thermal Amber
 */

export const colors = {
  // Core Neutral Surfaces
  void: "#070B12",
  graphite: "#0C1420",
  tertiary: "#101B29",
  elevated: "#142131",
  elevatedHover: "#192A3C",
  
  // Borders
  borderPrimary: "#243548",
  borderSubtle: "#1B2A39",

  // Typography
  textPrimary: "#EDF4FA",
  textSecondary: "#A5B5C5",
  textMuted: "#71869A",
  textDisabled: "#536477",

  // Semantic Accents
  cyan: {
    ion: "#63DDF2",      // Primary electrical intelligence
    bright: "#8BEAFF",   // High-contrast emphasis & focus rings
    deep: "#164F60",     // Glow fills & structural backdrops
  },
  amber: {
    thermal: "#FFB65C",  // Thermal intelligence & estimated temperatures
    orange: "#FF8955",   // Thermal gradient highlights
  },
  coral: {
    alert: "#FF647C",    // Precursor anomalies, warning states & threshold excursions
  },
  mint: {
    signal: "#83D9B2",   // Configured normal condition (never "safe")
  },
  blue: {
    info: "#7DAFFF",     // Informational & analytical metadata
  },
} as const;

export type ColorToken = typeof colors;

