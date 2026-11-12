import type { Metadata } from "next";
import "./globals.css";
import { ObservatoryNavbar } from "@/components/ObservatoryNavbar";

export const metadata: Metadata = {
  title: "SAGE: Empirical AI Safety & Agent Growth Observatory",
  description: "Measuring Security Drift, Capability Retention, and Specification Gaming in Self-Evolving Code Agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen text-slate-100 bg-[#090e1a] flex flex-col antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        {/* Innovative Top Horizon Command Deck & Floating Stage Navigator */}
        <ObservatoryNavbar />

        {/* Cinematic Full-Widescreen Canvas (No cramped 260px sidebar!) */}
        <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 pb-20">
          {children}
        </main>
      </body>
    </html>
  );
}
