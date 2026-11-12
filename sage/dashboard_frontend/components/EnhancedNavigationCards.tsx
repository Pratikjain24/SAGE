"use client";

import React, { useRef, useState } from "react";
import Link from "next/link";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ArrowRight, LucideIcon } from "lucide-react";

interface NavCard {
  href: string;
  title: string;
  subtitle: string;
  metric: string;
  badge: string;
  icon: LucideIcon;
  color: string;
  borderColor: string;
  bgHover: string;
  gradient: string;
}

interface EnhancedNavigationCardsProps {
  cards: NavCard[];
}

const MagneticCard: React.FC<{
  card: NavCard;
  index: number;
}> = ({ card, index }) => {
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseX = useSpring(x, { damping: 20, stiffness: 200 });
  const mouseY = useSpring(y, { damping: 20, stiffness: 200 });

  const rotateX = useTransform(mouseY, [-50, 50], [5, -5]);
  const rotateY = useTransform(mouseX, [-50, 50], [-5, 5]);

  const handleMouseMove = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set(e.clientX - centerX);
    y.set(e.clientY - centerY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const Icon = card.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="group"
    >
      <Link
        ref={ref}
        href={card.href}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="block relative"
      >
        <motion.div
          style={{
            rotateX,
            rotateY,
            transformStyle: "preserve-3d",
          }}
          className={`glass-card p-5 border ${card.borderColor} ${card.bgHover} transition-colors duration-300 flex flex-col justify-between h-full min-h-[180px] relative overflow-hidden`}
        >
          {/* Animated gradient overlay */}
          <div
            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            style={{
              background: card.gradient,
              mixBlendMode: "overlay",
            }}
          />

          {/* Content */}
          <div className="relative z-10">
            {/* Header with icon */}
            <div className="flex items-center justify-between mb-3">
              <motion.div
                className="p-2.5 rounded-xl bg-surface-3/80 border border-neon-cyan/20 group-hover:border-neon-cyan/50 transition-colors"
                whileHover={{ scale: 1.1, rotate: 360 }}
                transition={{ duration: 0.6 }}
                style={{ transformStyle: "preserve-3d", transform: "translateZ(20px)" }}
              >
                <Icon size={18} className={card.color} />
              </motion.div>
              <span className="text-[9px] font-mono text-slate-400 px-2 py-1 rounded-md bg-surface-3/60 border border-neon-cyan/10">
                {card.badge}
              </span>
            </div>

            {/* Title */}
            <h3 className="font-bold text-base text-white group-hover:text-neon-cyan transition-colors mb-2">
              {card.title}
            </h3>

            {/* Subtitle */}
            <p className="text-[11px] text-slate-400 leading-snug line-clamp-2 mb-3">
              {card.subtitle}
            </p>
          </div>

          {/* Footer with metric */}
          <div className="relative z-10 pt-3 mt-auto border-t border-neon-cyan/15 flex items-center justify-between text-xs font-mono">
            <span className={`font-bold ${card.color} text-[11px] line-clamp-1`}>
              {card.metric}
            </span>
            <motion.div
              className="text-slate-500 group-hover:text-neon-cyan transition-colors"
              animate={{ x: [0, 5, 0] }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <ArrowRight size={14} />
            </motion.div>
          </div>

          {/* Hover glow effect */}
          <div
            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
            style={{
              background: `radial-gradient(circle at 50% 50%, ${card.color.replace("text-", "rgba(")}0.1), transparent 70%)`,
              filter: "blur(20px)",
            }}
          />
        </motion.div>
      </Link>
    </motion.div>
  );
};

export const EnhancedNavigationCards: React.FC<EnhancedNavigationCardsProps> = ({ cards }) => {
  return (
    <div className="space-y-4">
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <span className="section-label">
            Interactive Deep-Dive Portals
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight mt-1">
            Explore Empirical Investigations & Analytical Graphs
          </h2>
        </div>
        <motion.span
          className="text-xs font-mono text-slate-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Click any card to inspect full dedicated page
        </motion.span>
      </motion.div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {cards.map((card, index) => (
          <MagneticCard key={card.href} card={card} index={index} />
        ))}
      </div>
    </div>
  );
};
