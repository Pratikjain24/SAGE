# SAGE Dashboard UI Enhancement - Implementation Guide

## 🎯 Overview

This guide walks you through implementing the enhanced UI components to transform your SAGE dashboard from a generic AI-generated appearance to a unique, publication-ready interface.

---

## ✅ Prerequisites

All required packages are already installed:
- ✅ `framer-motion` v14.12.0
- ✅ `@react-spring/web` v10.1.2
- ✅ `recharts` v3.10.1
- ✅ `d3` v7.9.2
- ✅ `gsap` v3.15.1

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Update KPI Cards

**File:** `app/page.tsx`

Replace the import:
```tsx
// OLD
import { KpiCards } from "@/components/KpiCards";

// NEW
import { EnhancedKpiCards } from "@/components/EnhancedKpiCards";
```

Replace the component usage (around line 120):
```tsx
// OLD
<KpiCards
  successRate={0.509}
  safetyDrift={0.000}
  proxyGap={0.055}
  totalCost={8.45}
  totalRuns={35}
/>

// NEW
<EnhancedKpiCards
  successRate={0.509}
  safetyDrift={0.000}
  proxyGap={0.055}
  totalCost={8.45}
  totalRuns={35}
/>
```

**Result:** ✨ 3D tilt effects, animated counters, gradient progress bars

---

### Step 2: Update Navigation Cards

**File:** `app/page.tsx`

Add import at top:
```tsx
import { EnhancedNavigationCards } from "@/components/EnhancedNavigationCards";
```

Replace the existing navigation grid (around line 180):
```tsx
// OLD
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  {navCards.map((card) => (
    <Link key={card.href} href={card.href} className="hud-card...">
      {/* ... */}
    </Link>
  ))}
</div>

// NEW
<EnhancedNavigationCards cards={navCards.map(card => ({
  ...card,
  gradient: `radial-gradient(circle at 50% 50%, ${card.color.replace('text-', '')}20, transparent 70%)`
}))} />
```

**Result:** ✨ Magnetic 3D effects, animated gradients, smooth transitions

---

### Step 3: Update Data Table

**File:** `app/page.tsx`

Add import:
```tsx
import { EnhancedDataTable } from "@/components/EnhancedDataTable";
```

Replace the table section (around line 240):
```tsx
// OLD
<div className="hud-card p-6">
  <table className="w-full...">
    {/* ... */}
  </table>
</div>

// NEW
<EnhancedDataTable
  data={LAYERS_EMPIRICAL_DATA}
  title="Comparative Archetype Matrix (G₁ through G₇)"
  subtitle="5 Seeds per Layer • 9,800 Tasks"
/>
```

**Result:** ✨ Row hover effects, sortable columns, inline sparklines

---

### Step 4: Update Drift Curve (Drift Page)

**File:** `app/drift/page.tsx`

Replace import:
```tsx
// OLD
import { DriftCurve } from "@/components/DriftCurve";

// NEW
import { EnhancedDriftCurve } from "@/components/EnhancedDriftCurve";
```

Replace component usage:
```tsx
// OLD
<DriftCurve data={driftData} />

// NEW
<EnhancedDriftCurve data={driftData} />
```

**Result:** ✨ Animated path drawing, particle effects, gradient fills

---

## 🎨 Full Integration (30 Minutes)

### Phase 1: Core Components (10 min)

1. **Update all KPI card instances**
   - `app/page.tsx`
   - `app/capability/page.tsx`
   - `app/pareto/page.tsx`

2. **Update all navigation sections**
   - `app/page.tsx` (main dashboard)
   - Any landing pages

3. **Update all data tables**
   - `app/page.tsx` (archetype matrix)
   - `app/leaderboard/page.tsx`

### Phase 2: Chart Components (15 min)

Replace chart components in these pages:

| Page | Old Component | New Component |
|------|--------------|---------------|
| `app/drift/page.tsx` | `DriftCurve` | `EnhancedDriftCurve` |
| `app/capability/page.tsx` | `CapabilityTrajectories` | Create enhanced version |
| `app/pareto/page.tsx` | `ParetoFrontier` | Create enhanced version |
| `app/proxy-gap/page.tsx` | `ProxyGapChart` | Create enhanced version |

### Phase 3: Testing (5 min)

```bash
cd sage\dashboard_frontend
npm run dev
```

Visit:
- http://localhost:3000 (main dashboard)
- http://localhost:3000/drift
- http://localhost:3000/capability

---

## 🎯 Per-Page Implementation

### Homepage (`app/page.tsx`)

**Changes Required:**
1. Import enhanced components
2. Replace KPI cards
3. Replace navigation cards
4. Replace archetype table
5. Update quick stats bar

**Estimated Time:** 10 minutes

**Expected Visual Changes:**
- ✨ 3D cards with tilt effects
- ✨ Animated counters
- ✨ Gradient progress bars
- ✨ Magnetic navigation cards
- ✨ Sortable table with sparklines

---

### Drift Page (`app/drift/page.tsx`)

**Changes Required:**
1. Replace `DriftCurve` with `EnhancedDriftCurve`
2. Update page wrapper for consistent glassmorphism

**Estimated Time:** 3 minutes

**Expected Visual Changes:**
- ✨ Animated curve drawing (1.5s)
- ✨ Particle effects on hover
- ✨ Gradient CI bands
- ✨ Glow effects on active curves

---

### Capability Page (`app/capability/page.tsx`)

**Status:** ⚠️ Needs new enhanced component

**Next Steps:**
1. Create `EnhancedCapabilityTrajectories.tsx` based on `EnhancedDriftCurve.tsx`
2. Add dual-axis support (train vs test)
3. Implement interactive legend filtering

---

### Pareto Frontier (`app/pareto/page.tsx`)

**Status:** ⚠️ Needs new enhanced component

**Next Steps:**
1. Create `EnhancedParetoFrontier.tsx` with Recharts
2. Implement bubble size/color encoding
3. Add zoom/pan interactions
4. Include convex hull highlighting

---

### Proxy Gap (`app/proxy-gap/page.tsx`)

**Status:** ⚠️ Needs new enhanced component

**Next Steps:**
1. Create `EnhancedProxyGapChart.tsx`
2. Animated bar chart with gradient fills
3. Add comparison mode toggle
4. Implement micro-interactions on bars

---

## 🔧 Customization Guide

### Adjusting Colors

**File:** `tailwind.config.js`

```js
neon: {
  cyan: "#00f0ff",     // Change primary accent
  purple: "#b847ff",   // Change secondary
  // ...
}
```

### Adjusting Animation Speed

**Global Speed:**
```tsx
// In any component
transition={{ duration: 0.6 }} // Increase/decrease
```

**Disable Animations:**
Add to `globals.css`:
```css
* {
  animation: none !important;
  transition: none !important;
}
```

### Adjusting 3D Intensity

**File:** `components/EnhancedKpiCards.tsx`

```tsx
// Line ~85
setRotateX(-(mouseY / rect.height) * 5);  // Reduce from 10 to 5
setRotateY((mouseX / rect.width) * 5);    // Reduce from 10 to 5
```

---

## 🐛 Troubleshooting

### Issue: "Module not found: Can't resolve 'framer-motion'"

**Solution:**
```bash
npm install framer-motion @react-spring/web recharts d3 gsap
```

### Issue: TypeScript errors for motion components

**Solution:**
Add to `tsconfig.json`:
```json
{
  "compilerOptions": {
    "skipLibCheck": true
  }
}
```

### Issue: Animations are laggy

**Solutions:**
1. Check browser DevTools Performance tab
2. Reduce number of animated elements
3. Use `will-change: transform` sparingly
4. Enable GPU acceleration:
```css
.animated-element {
  transform: translateZ(0);
}
```

### Issue: Glassmorphism not working

**Check:**
1. Browser supports `backdrop-filter` (all modern browsers do)
2. Parent element has background content
3. No `overflow: hidden` blocking blur

---

## 📊 Performance Checklist

Before deploying:

- [ ] Run Lighthouse audit (target: 90+ performance)
- [ ] Test on mobile devices
- [ ] Check reduced-motion preference
- [ ] Verify animations at 60fps (Chrome DevTools)
- [ ] Test keyboard navigation
- [ ] Validate ARIA labels
- [ ] Check color contrast ratios (WCAG AA)

**Tools:**
```bash
# Lighthouse
npx lighthouse http://localhost:3000 --view

# Bundle size
npm run build
# Check .next/static/* sizes
```

---

## 🚢 Deployment Checklist

### Pre-Deploy
- [ ] All components tested locally
- [ ] No console errors
- [ ] Mobile responsive verified
- [ ] Accessibility audit passed
- [ ] Performance metrics green

### Build
```bash
npm run build
npm run start  # Test production build locally
```

### Deploy
```bash
# Vercel (recommended)
vercel --prod

# Or manual
npm run build
# Upload .next/ folder to hosting
```

---

## 📈 Migration Path

### Conservative (Gradual)
**Week 1:** Homepage KPI cards + navigation  
**Week 2:** All tables  
**Week 3:** Drift curve  
**Week 4:** Remaining charts  

### Aggressive (All at once)
**Day 1:** Replace all components  
**Day 2:** Test and fix issues  
**Day 3:** Deploy  

**Recommended:** Conservative for production, Aggressive for research demo

---

## 🎓 Learning Resources

### Framer Motion
- [Animation Controls](https://www.framer.com/motion/animation/)
- [Gestures](https://www.framer.com/motion/gestures/)
- [Layout Animations](https://www.framer.com/motion/layout-animations/)

### React Spring
- [UseSpring Hook](https://www.react-spring.dev/docs/components/use-spring)
- [Physics Config](https://www.react-spring.dev/docs/advanced/config)

### D3
- [Scales](https://d3js.org/d3-scale)
- [Shapes](https://d3js.org/d3-shape)

---

## 💡 Pro Tips

1. **Stagger Delays:** Use `index * 0.1` for smooth sequential animations
2. **Spring Physics:** `damping: 20, stiffness: 200` feels natural
3. **Hover Glows:** Keep opacity low (0.2-0.4) for subtlety
4. **3D Effects:** Limit rotation to ±10deg to avoid motion sickness
5. **Particle Effects:** Keep duration short (0.6-0.8s) to avoid clutter

---

## 🎉 Next Steps

After implementing the core enhancements:

1. **Create remaining enhanced charts:**
   - CapabilityTrajectories
   - ParetoFrontier
   - ProxyGapChart
   - CycleHeatmap

2. **Add advanced features:**
   - Dark/light mode toggle
   - Export chart as SVG/PNG
   - Interactive data filtering
   - Real-time updates

3. **Optimize for production:**
   - Code splitting
   - Image optimization
   - CDN for static assets

---

## 📞 Support

**Issues?** Check:
1. This guide's Troubleshooting section
2. STYLE_GUIDE.md for component specs
3. Component source code comments

**Questions?**
Open an issue with:
- Screenshot of the problem
- Browser console errors
- Steps to reproduce

---

**Happy building! 🚀✨**
