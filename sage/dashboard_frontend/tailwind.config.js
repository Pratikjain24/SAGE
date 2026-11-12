/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0a0118",
        surface: {
          0: "#0a0118",
          1: "#0f0520",
          2: "#160a2e",
          3: "#1d0f3d",
          4: "#25154d",
        },
        // Neon accent system
        neon: {
          cyan: "#00f0ff",
          purple: "#b847ff",
          pink: "#ff00e5",
          green: "#00ff9f",
          blue: "#0066ff",
        },
        accent: {
          DEFAULT: "#00f0ff",
          hover: "#33f3ff",
          glow: "rgba(0, 240, 255, 0.4)",
        },
        brand: {
          cyan: "#00f0ff",
          blue: "#0066ff",
          emerald: "#00ff9f",
          amber: "#ffa600",
          rose: "#ff0055",
          purple: "#b847ff",
        },
        group: {
          G1: "#94a3b8",
          G2: "#0066ff",
          G3: "#00ff9f",
          G4: "#ffa600",
          G5: "#b847ff",
          G6: "#ff00e5",
          G7: "#00f0ff",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
        display: ["Space Grotesk", "Inter", "sans-serif"],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'radial-gradient(at 20% 30%, rgba(184, 71, 255, 0.12) 0px, transparent 50%), radial-gradient(at 80% 70%, rgba(0, 240, 255, 0.08) 0px, transparent 50%), radial-gradient(at 50% 50%, rgba(0, 255, 159, 0.05) 0px, transparent 50%)',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 240, 255, 0.4), 0 0 40px rgba(0, 240, 255, 0.2)',
        'glow-purple': '0 0 20px rgba(184, 71, 255, 0.4), 0 0 40px rgba(184, 71, 255, 0.2)',
        'glow-green': '0 0 20px rgba(0, 255, 159, 0.4), 0 0 40px rgba(0, 255, 159, 0.2)',
        'glow-pink': '0 0 20px rgba(255, 0, 229, 0.4), 0 0 40px rgba(255, 0, 229, 0.2)',
        'inner-glow': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.1)',
      },
      backdropBlur: {
        xs: '2px',
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideInLeft: {
          "0%": { opacity: "0", transform: "translateX(-30px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(30px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        pulseSlow: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        gradientShift: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(0, 240, 255, 0.3), 0 0 40px rgba(0, 240, 255, 0.1)" },
          "50%": { boxShadow: "0 0 30px rgba(0, 240, 255, 0.5), 0 0 60px rgba(0, 240, 255, 0.2)" },
        },
        borderGlow: {
          "0%, 100%": { borderColor: "rgba(0, 240, 255, 0.3)" },
          "50%": { borderColor: "rgba(0, 240, 255, 0.8)" },
        },
        rotate360: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "slide-in-left": "slideInLeft 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "slide-in-right": "slideInRight 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "scale-in": "scaleIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "float": "float 3s ease-in-out infinite",
        "pulse-slow": "pulseSlow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2.5s infinite linear",
        "gradient-shift": "gradientShift 8s ease infinite",
        "glow": "glowPulse 3s ease-in-out infinite",
        "border-glow": "borderGlow 2s ease-in-out infinite",
        "spin-slow": "rotate360 8s linear infinite",
      },
    },
  },
  plugins: [],
};
