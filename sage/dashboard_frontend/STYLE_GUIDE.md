# SAGE Dashboard - Living Style Guide

**Version:** 2.0 Enhanced Edition  
**Last Updated:** 2026-11-11  
**Status:** 🎨 Production-Ready

---

## 🎨 Design Philosophy

The SAGE dashboard embodies a **deep space aesthetic** with **neon cyberpunk accents**, creating a unique, publication-ready interface that stands apart from generic AI-generated UIs.

### Core Principles
1. **Glassmorphism First** - Semi-transparent surfaces with backdrop blur
2. **Neon Accents** - Cyan, purple, pink, and green highlights
3. **Smooth Animations** - 60fps GPU-accelerated transitions
4. **3D Depth** - Subtle parallax and perspective transforms
5. **Data Clarity** - Beautiful doesn't sacrifice readability

---

## 🎨 Color System

### Background Layers
```css
--surface-0: #0a0118  /* Deep space black */
--surface-1: #0f0520  /* Primary background */
--surface-2: #160a2e  /* Card background */
--surface-3: #1d0f3d  /* Elevated surfaces */
--surface-4: #25154d  /* Highest elevation */
```

### Neon Accent Palette
```css
--neon-cyan: #00f0ff    /* Primary accent */
--neon-purple: #b847ff  /* Secondary accent */
--neon-pink: #ff00e5    /* Tertiary accent */
--neon-green: #00ff9f   /* Success/safe */
--neon-blue: #0066ff    /* Info */
```

### Semantic Colors
```css
--safe: #00ff9f      /* Security OK, zero drift */
--drift: #ff0055     /* Security violations */
--warn: #ffa600      /* Warnings, proxy gap */
```

### Archetype Colors (G₁-G₇)
```css
G1: #94a3b8  /* Frozen Baseline - gray */
G2: #0066ff  /* Prompt Rewriter - blue */
G3: #00ff9f  /* Memory Accumulator - green */
G4: #ffa600  /* Reflection Agent - amber */
G5: #b847ff  /* Static Verifier - purple */
G6: #ff00e5  /* Regression Guard - pink */
G7: #00f0ff  /* Proxy Canary Guard - cyan */
```

---

## 📦 Component Library

### 1. Glass Cards

#### **Basic Glass Card**
```tsx
<div className="glass-card p-6">
  {/* Content */}
</div>
```

**Features:**
- Semi-transparent background with backdrop blur
- Animated shimmer effect on hover
- Subtle inner glow
- Smooth scale transform

**CSS:**
```css
.glass-card {
  background: rgba(22, 10, 46, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 240, 255, 0.15);
  border-radius: 16px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
}
```

#### **HUD Card**
```tsx
<div className="hud-card p-5">
  {/* Metrics and data */}
</div>
```

**Features:**
- Gradient background
- Border glow on hover
- Optimized for KPI displays

---

### 2. Enhanced KPI Cards

**Import:**
```tsx
import { EnhancedKpiCards } from "@/components/EnhancedKpiCards";
```

**Usage:**
```tsx
<EnhancedKpiCards
  successRate={0.509}
  safetyDrift={0.000}
  proxyGap={0.055}
  totalCost={8.45}
  totalRuns={35}
/>
```

**Features:**
- 3D tilt effect on mouse move
- Animated counters with spring physics
- Gradient progress bars with shimmer
- Icon rotation on hover
- Staggered entrance animations

---

### 3. Enhanced Drift Curve

**Import:**
```tsx
import { EnhancedDriftCurve } from "@/components/EnhancedDriftCurve";
```

**Features:**
- Animated path drawing (1.5s duration)
- Particle effects on hover
- Interactive legend with glow effects
- Gradient CI bands
- Smooth transitions between states

**Interactions:**
- Hover over legend buttons to highlight curve
- Hover over data points for tooltip + particles
- Click legend to lock selection

---

### 4. Enhanced Data Table

**Import:**
```tsx
import { EnhancedDataTable } from "@/components/EnhancedDataTable";
```

**Features:**
- Row hover with scale and glow
- Sortable columns with animated icon
- Inline sparklines for trends
- Staggered row entrance
- Color-coded metrics

**Sorting:**
Click any column header with the sort icon to toggle:
- First click: Descending
- Second click: Ascending
- Third click: No sort (original order)

---

### 5. Enhanced Navigation Cards

**Import:**
```tsx
import { EnhancedNavigationCards } from "@/components/EnhancedNavigationCards";
```

**Features:**
- Magnetic 3D tilt effect (follows mouse)
- Gradient overlay on hover
- Animated arrow pulse
- Icon rotation animation
- Staggered entrance

---

## 🎬 Animation Tokens

### Timing Functions
```css
--ease-smooth: cubic-bezier(0.16, 1, 0.3, 1)  /* Smooth ease-out */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55)  /* Overshoot */
```

### Duration Scale
```css
--duration-instant: 0.15s
--duration-fast: 0.3s
--duration-normal: 0.5s
--duration-slow: 0.8s
--duration-slower: 1.2s
```

### Keyframe Animations

#### **Fade In Up**
```css
@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
```

#### **Gradient Shift**
```css
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

#### **Glow Pulse**
```css
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 240, 255, 0.3); }
  50% { box-shadow: 0 0 30px rgba(0, 240, 255, 0.5); }
}
```

---

## 🔤 Typography

### Font Stack
```css
--font-sans: 'Inter', -apple-system, sans-serif
--font-mono: 'JetBrains Mono', monospace
--font-display: 'Space Grotesk', 'Inter', sans-serif
```

### Type Scale
```css
.section-label {
  font-family: var(--font-mono);
  font-size: 0.6875rem;  /* 11px */
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--neon-cyan);
}

h1 { font-size: 2rem; font-weight: 900; }
h2 { font-size: 1.5rem; font-weight: 800; }
h3 { font-size: 1.25rem; font-weight: 700; }
```

---

## 🎯 Interactive Elements

### Buttons

#### **Primary Button**
```tsx
<button className="btn-primary">
  Launch Analysis
  <ArrowRight size={14} />
</button>
```

**Features:**
- Gradient background (cyan to blue)
- Shimmer effect on hover
- Scale transform
- Inner glow

#### **Secondary Button**
```tsx
<button className="btn-secondary">
  View Details
</button>
```

**Features:**
- Glassmorphism style
- Border glow on hover
- Subtle scale

---

### Status Indicators

#### **Safe Indicator**
```tsx
<span className="indicator-safe">
  ✓ Zero Drift
</span>
```

#### **Drift Indicator**
```tsx
<span className="indicator-drift">
  ⚠ Drift Alert
</span>
```

#### **Metric Tag**
```tsx
<span className="metric-tag">
  Formula: Δ Violations(t)
</span>
```

---

## 📊 Chart Guidelines

### Color Encoding
- **Green (#00ff9f):** Success, safe operations, zero drift
- **Cyan (#00f0ff):** Primary metrics, G7 archetype
- **Amber (#ffa600):** Warnings, moderate drift
- **Red (#ff0055):** Errors, high drift, violations
- **Purple (#b847ff):** Advanced features, G5 archetype

### Animation Best Practices
1. **Path Drawing:** 1-2 second duration for smooth reveal
2. **Particle Effects:** 0.8s fade-out with scale
3. **Hover Transitions:** 0.2-0.3s for responsiveness
4. **Data Updates:** Spring physics for organic movement

### Accessibility
- All charts include tooltips with keyboard navigation
- Color is not the only differentiator (patterns, labels, icons)
- Reduced motion support via `prefers-reduced-motion`

---

## 🎭 Motion System

### Entrance Animations

**Staggered Cards:**
```tsx
{cards.map((card, i) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: i * 0.1, duration: 0.6 }}
  >
    {card}
  </motion.div>
))}
```

**Fade In:**
```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.5 }}
>
```

### Hover Effects

**3D Tilt:**
```tsx
<motion.div
  onMouseMove={handleMouseMove}
  onMouseLeave={handleMouseLeave}
  style={{
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
  }}
>
```

**Magnetic Pull:**
```tsx
const x = useSpring(0, { damping: 20, stiffness: 200 });
const y = useSpring(0, { damping: 20, stiffness: 200 });
```

---

## ♿ Accessibility

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Keyboard Navigation
- All interactive elements are focusable
- Tab order follows visual hierarchy
- Focus indicators with neon glow

### ARIA Labels
```tsx
<button aria-label="Sort by archetype ID">
  <ArrowUpDown size={12} />
</button>
```

---

## 🚀 Performance

### Optimization Checklist
- ✅ GPU-accelerated transforms (transform, opacity)
- ✅ Backdrop-filter with `will-change` hint
- ✅ Debounced mouse tracking
- ✅ Lazy loading for off-screen charts
- ✅ CSS containment for isolated animations

### Target Metrics
- **FPS:** 60fps during animations
- **LCP:** < 2.5s
- **CLS:** < 0.1
- **FID:** < 100ms

---

## 📦 Component Checklist

Before publishing a new component:

- [ ] Implements glassmorphism design system
- [ ] Uses neon accent colors appropriately
- [ ] Includes entrance animation
- [ ] Has hover/focus states
- [ ] Supports reduced motion
- [ ] Mobile responsive
- [ ] TypeScript types defined
- [ ] Accessible ARIA labels
- [ ] Documented in this guide

---

## 🎨 Theme Variants

### Dark Mode (Default)
Current implementation. Deep space purple with neon accents.

### Light Mode (Future)
Not yet implemented. Would use:
- Base: #f8f9fb
- Surface: #ffffff with 0.8 opacity
- Accents: Same neon colors at 80% saturation

---

## 📝 Code Standards

### Import Order
```tsx
// 1. React
import React from "react";

// 2. External libraries
import { motion } from "framer-motion";

// 3. Internal components
import { KpiCards } from "@/components/KpiCards";

// 4. Types
import { CycleMetricPoint } from "@/lib/api";

// 5. Assets
import "./styles.css";
```

### Component Structure
```tsx
interface Props { /* ... */ }

export const ComponentName: React.FC<Props> = ({ prop1, prop2 }) => {
  // 1. Hooks
  const [state, setState] = useState();
  
  // 2. Refs
  const ref = useRef();
  
  // 3. Effects
  useEffect(() => {}, []);
  
  // 4. Handlers
  const handleClick = () => {};
  
  // 5. Render
  return <div />;
};
```

---

## 🔗 Resources

- **Framer Motion Docs:** https://www.framer.com/motion/
- **Tailwind CSS:** https://tailwindcss.com
- **Recharts:** https://recharts.org
- **GSAP:** https://greensock.com/gsap/

---

**Made with 💜 for publication-ready research dashboards**
