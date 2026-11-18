/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core Neutral Palette
        void: "#070B12",
        graphite: "#0C1420",
        tertiary: "#101B29",
        elevated: {
          DEFAULT: "#142131",
          hover: "#192A3C",
        },
        border: {
          DEFAULT: "#243548",
          primary: "#243548",
          subtle: "#1B2A39",
        },
        text: {
          primary: "#EDF4FA",
          secondary: "#A5B5C5",
          muted: "#71869A",
          disabled: "#536477",
        },

        // Semantic Accents
        cyan: {
          ion: "#63DDF2",
          bright: "#8BEAFF",
          deep: "#164F60",
        },
        amber: {
          thermal: "#FFB65C",
          orange: "#FF8955",
        },
        coral: {
          alert: "#FF647C",
        },
        mint: {
          signal: "#83D9B2",
        },
        blue: {
          info: "#7DAFFF",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "Sora", "sans-serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      fontSize: {
        "display-xl": ["4.5rem", { lineHeight: "1.05", letterSpacing: "-0.03em" }],
        "display-l": ["3.25rem", { lineHeight: "1.1", letterSpacing: "-0.025em" }],
        "h1": ["2.25rem", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
        "h2": ["1.875rem", { lineHeight: "1.25", letterSpacing: "-0.015em" }],
        "h3": ["1.5rem", { lineHeight: "1.3", letterSpacing: "-0.01em" }],
        "h4": ["1.25rem", { lineHeight: "1.35", letterSpacing: "-0.005em" }],
        "body-lg": ["1.0625rem", { lineHeight: "1.5" }],
        "body": ["0.9375rem", { lineHeight: "1.55" }],
        "caption": ["0.8125rem", { lineHeight: "1.4" }],
        "technical": ["0.6875rem", { lineHeight: "1.3", letterSpacing: "0.08em" }],
      },
      borderRadius: {
        control: "8px",
        input: "10px",
        panel: "14px",
        card: "18px",
        mega: "20px",
      },
      boxShadow: {
        subtle: "0 4px 20px -2px rgba(7, 11, 18, 0.7)",
        elevated: "0 8px 30px -4px rgba(7, 11, 18, 0.85)",
        floating: "0 20px 40px -10px rgba(0, 0, 0, 0.9)",
        "cyan-glow": "0 0 25px -5px rgba(99, 221, 242, 0.25)",
        "amber-glow": "0 0 25px -5px rgba(255, 182, 92, 0.25)",
        "coral-glow": "0 0 25px -5px rgba(255, 100, 124, 0.25)",
      },
      backgroundImage: {
        "grid-pattern": "linear-gradient(to right, #1B2A39 1px, transparent 1px), linear-gradient(to bottom, #1B2A39 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};

