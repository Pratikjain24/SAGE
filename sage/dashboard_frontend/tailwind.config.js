/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#070a12",
        surface: {
          0: "#070a12",
          1: "#0b101c",
          2: "#0f1626",
          3: "#151f35",
          4: "#1c2944",
        },
        accent: {
          DEFAULT: "#38bdf8", // Sky / cyan accent
          hover: "#60a5fa",
          glow: "rgba(56, 189, 248, 0.25)",
        },
        brand: {
          cyan: "#06b6d4",
          blue: "#3b82f6",
          emerald: "#10b981",
          amber: "#f59e0b",
          rose: "#ef4444",
          purple: "#8b5cf6",
        },
        group: {
          G1: "#94a3b8",
          G2: "#3b82f6",
          G3: "#10b981",
          G4: "#f59e0b",
          G5: "#8b5cf6",
          G6: "#ec4899",
          G7: "#06b6d4",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        pulseSlow: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(1000%)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 15px rgba(6, 182, 212, 0.3)" },
          "50%": { boxShadow: "0 0 25px rgba(6, 182, 212, 0.6)" },
        },
      },
      animation: {
        "fade-in-up": "fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "fade-in": "fadeIn 0.3s ease-out forwards",
        "pulse-slow": "pulseSlow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2.5s infinite linear",
        "scan": "scanline 8s linear infinite",
        "glow": "glowPulse 3s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
