/**
 * HeatSense Motion & Transition Tokens
 * Precision Framer Motion animation configurations
 */

export const motionTokens = {
  durations: {
    micro: 0.15,      // 150ms for buttons, hover states
    standard: 0.22,   // 220ms for menu dropdowns, cards
    expanded: 0.35,   // 350ms for modals, drawers
    cinematic: 0.6,   // 600ms for hero/3D transitions
  },
  easings: {
    snappy: [0.16, 1, 0.3, 1] as const,     // Linear/Apple style snap
    smooth: [0.25, 0.1, 0.25, 1] as const,  // Material cubic
    dramatic: [0.7, 0, 0.84, 0] as const,
  },
  variants: {
    fadeIn: {
      initial: { opacity: 0 },
      animate: { opacity: 1, transition: { duration: 0.22, ease: [0.16, 1, 0.3, 1] } },
      exit: { opacity: 0, transition: { duration: 0.15 } },
    },
    slideDownFade: {
      initial: { opacity: 0, y: -8 },
      animate: { opacity: 1, y: 0, transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] } },
      exit: { opacity: 0, y: -6, transition: { duration: 0.15 } },
    },
    scaleUpFade: {
      initial: { opacity: 0, scale: 0.96 },
      animate: { opacity: 1, scale: 1, transition: { duration: 0.22, ease: [0.16, 1, 0.3, 1] } },
      exit: { opacity: 0, scale: 0.96, transition: { duration: 0.15 } },
    },
  },
};

