import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { FloatingNav, CommandPalette, MobileNav } from "../components/navigation";
import { ShieldCheck, Cpu } from "lucide-react";

export const App: React.FC = () => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  // Global hotkey listener for Cmd+K / Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="relative min-h-screen bg-hs-void text-hs-text-primary font-sans antialiased selection:bg-hs-cyan-ion/25 selection:text-hs-cyan-bright overflow-x-hidden">
      {/* Background Engineering Grid and Atmospheric Radial Light Field */}
      <div className="fixed inset-0 bg-hs-engineering-grid opacity-25 pointer-events-none" />
      <div className="fixed top-[-10%] left-[20%] w-[60vw] h-[50vh] rounded-full bg-hs-cyan-deep/10 blur-[140px] pointer-events-none" />
      <div className="fixed bottom-[-10%] right-[15%] w-[45vw] h-[40vh] rounded-full bg-hs-amber-thermal/5 blur-[160px] pointer-events-none" />

      {/* Floating MegaNav Header */}
      <FloatingNav
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onOpenMobileNav={() => setIsMobileNavOpen(true)}
      />

      {/* Mobile Responsive Drawer */}
      <MobileNav
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      {/* Global Command Palette Modal */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />

      {/* Main Experience Viewport Container */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 pt-24 sm:pt-28 pb-16">
        <Outlet />
      </main>

      {/* Industrial Engineering Footer */}
      <footer className="relative z-10 border-t border-hs-border-primary/50 bg-hs-graphite/70 backdrop-blur-md mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-mono text-hs-text-muted">
          <div className="flex items-center gap-3">
            <span className="font-bold tracking-widest text-hs-text-secondary">
              HEATSENSE
            </span>
            <span className="text-hs-border-primary">|</span>
            <span>PHYSICS-INFORMED BATTERY DIGITAL TWIN</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 text-[11px]">
            <div className="flex items-center gap-1.5 text-hs-mint-signal">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Firmware Relay Cutoff Authority</span>
            </div>
            <span className="text-hs-border-primary hidden sm:inline">•</span>
            <div className="flex items-center gap-1.5 text-hs-text-muted">
              <Cpu className="w-3.5 h-3.5 text-hs-cyan-ion" />
              <span>Host Advisory Architecture</span>
            </div>
            <span className="text-hs-border-primary hidden sm:inline">•</span>
            <span className="text-hs-text-muted">Single 18650 Li-ion Cell</span>
          </div>

          <div className="text-[11px] text-hs-text-muted/60">
            Phase 3.0 Foundation Active
          </div>
        </div>
      </footer>
    </div>
  );
};
