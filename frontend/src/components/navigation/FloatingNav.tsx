import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Search, Menu, ChevronDown, Activity } from "lucide-react";
import { NAV_GROUPS } from "./navData";
import { StatusIndicator } from "../ui/StatusIndicator";

interface FloatingNavProps {
  onOpenCommandPalette: () => void;
  onOpenMobileNav: () => void;
}

export const FloatingNav: React.FC<FloatingNavProps> = ({
  onOpenCommandPalette,
  onOpenMobileNav,
}) => {
  const [activeGroup, setActiveGroup] = useState<string | null>(null);
  const location = useLocation();
  const navRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Close mega menu on route change
  useEffect(() => {
    setActiveGroup(null);
  }, [location.pathname]);

  // Handle mouse enter with debounce protection
  const handleMouseEnter = (groupName: string) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setActiveGroup(groupName);
  };

  // Handle mouse leave with delay so user can easily mouse into the dropdown
  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setActiveGroup(null);
    }, 180);
  };

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setActiveGroup(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <header className="fixed top-3 sm:top-4 left-0 right-0 z-40 flex justify-center px-3 sm:px-6 pointer-events-none">
      <div
        ref={navRef}
        onMouseLeave={handleMouseLeave}
        className="pointer-events-auto relative w-full max-w-7xl bg-hs-graphite/90 border border-hs-border-primary/80 backdrop-blur-xl rounded-2xl shadow-[0_12px_36px_rgba(0,0,0,0.65)] px-3.5 sm:px-5 py-2.5 transition-all duration-200"
      >
        <div className="flex items-center justify-between gap-4">
          {/* Brand Mark */}
          <Link
            to="/command-centre"
            className="flex items-center gap-2.5 group select-none shrink-0"
          >
            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-hs-cyan-deep/40 border border-hs-cyan-ion/40 shadow-[0_0_12px_rgba(99,221,242,0.3)] transition-all group-hover:border-hs-cyan-ion group-hover:shadow-[0_0_18px_rgba(99,221,242,0.5)]">
              <Activity className="w-4 h-4 text-hs-cyan-bright transition-transform group-hover:scale-110" />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-hs-mint-signal animate-pulse" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-mono font-bold tracking-wider text-sm sm:text-base text-hs-text-primary group-hover:text-hs-cyan-bright transition-colors">
                  HEATSENSE
                </span>
                <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-hs-cyan-deep/30 text-hs-cyan-bright border border-hs-cyan-ion/25 hidden lg:inline">
                  v3.0
                </span>
              </div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-hs-text-muted hidden sm:inline">
                Battery Intelligence
              </span>
            </div>
          </Link>

          {/* Desktop MegaNav Groups */}
          <nav
            className="hidden md:flex items-center gap-1 lg:gap-2"
            role="navigation"
            aria-label="Main Navigation"
          >
            {NAV_GROUPS.map((group) => {
              const isGroupActive = group.items.some(
                (item) => item.path === location.pathname
              );
              const isOpen = activeGroup === group.name;

              return (
                <div
                  key={group.name}
                  className="relative"
                  onMouseEnter={() => handleMouseEnter(group.name)}
                >
                  <button
                    onClick={() =>
                      setActiveGroup(isOpen ? null : group.name)
                    }
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-sans transition-all ${
                      isOpen || isGroupActive
                        ? "bg-hs-elevated text-hs-cyan-bright border border-hs-cyan-ion/35 shadow-sm"
                        : "text-hs-text-secondary hover:text-hs-text-primary hover:bg-hs-elevated/60 border border-transparent"
                    }`}
                    aria-expanded={isOpen}
                  >
                    <span>{group.name}</span>
                    <ChevronDown
                      className={`w-3.5 h-3.5 transition-transform duration-200 ${
                        isOpen ? "rotate-180 text-hs-cyan-bright" : "text-hs-text-muted"
                      }`}
                    />
                  </button>

                  {/* MegaMenu Dropdown Panel */}
                  {isOpen && (
                    <div
                      className="absolute top-full left-0 sm:left-1/2 sm:-translate-x-1/2 pt-2 z-50 w-80 lg:w-96 animate-in fade-in slide-in-from-top-2 duration-150"
                      onMouseEnter={() => handleMouseEnter(group.name)}
                    >
                      <div className="bg-hs-graphite/95 border border-hs-border-primary rounded-xl shadow-[0_20px_45px_rgba(0,0,0,0.85)] p-2 backdrop-blur-2xl">
                        <div className="px-3 py-2 border-b border-hs-border-primary/60 mb-1">
                          <span className="text-[10px] font-mono uppercase tracking-wider text-hs-cyan-bright font-semibold">
                            {group.name} Environments
                          </span>
                          <p className="text-[11px] text-hs-text-muted mt-0.5">
                            {group.description}
                          </p>
                        </div>

                        <div className="space-y-1">
                          {group.items.map((item) => {
                            const Icon = item.icon;
                            const isCurrent = location.pathname === item.path;

                            return (
                              <Link
                                key={item.id}
                                to={item.path}
                                className={`flex items-start gap-3 p-2.5 rounded-lg transition-all group ${
                                  isCurrent
                                    ? "bg-hs-elevated text-hs-text-primary border border-hs-cyan-ion/40 shadow-sm"
                                    : "text-hs-text-secondary hover:bg-hs-elevated/60 hover:text-hs-text-primary border border-transparent"
                                }`}
                              >
                                <div
                                  className={`p-2 rounded-md shrink-0 transition-colors ${
                                    isCurrent
                                      ? "bg-hs-cyan-deep/40 text-hs-cyan-bright"
                                      : "bg-hs-elevated text-hs-text-muted group-hover:text-hs-cyan-bright group-hover:bg-hs-cyan-deep/20"
                                  }`}
                                >
                                  <Icon className="w-4 h-4" />
                                </div>
                                <div className="flex flex-col min-w-0">
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-semibold text-hs-text-primary group-hover:text-hs-cyan-bright transition-colors truncate">
                                      {item.title}
                                    </span>
                                    {item.badge && (
                                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-hs-void text-hs-text-muted border border-hs-border-subtle shrink-0">
                                        {item.badge}
                                      </span>
                                    )}
                                  </div>
                                  <span className="text-[11px] text-hs-text-muted line-clamp-1 mt-0.5">
                                    {item.description}
                                  </span>
                                </div>
                              </Link>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </nav>

          {/* Right Section: System Status + Command Palette Trigger + Mobile Toggle */}
          <div className="flex items-center gap-2.5">
            {/* Live System Status Indicator */}
            <div className="hidden lg:flex items-center">
              <StatusIndicator status="normal" size="sm" pulse />
            </div>

            {/* Quick Command Palette Button */}
            <button
              onClick={onOpenCommandPalette}
              className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-lg bg-hs-elevated/80 border border-hs-border-primary text-hs-text-muted hover:text-hs-text-primary hover:border-hs-cyan-ion/40 transition-all text-xs font-sans shadow-sm"
              title="Search and Quick Commands (Ctrl+K)"
            >
              <Search className="w-3.5 h-3.5 text-hs-cyan-ion" />
              <span className="hidden sm:inline text-hs-text-secondary text-xs">
                Jump to...
              </span>
              <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded bg-hs-void border border-hs-border-subtle font-mono text-[10px] text-hs-text-muted">
                ⌘K
              </kbd>
            </button>

            {/* Mobile Hamburger Trigger */}
            <button
              onClick={onOpenMobileNav}
              className="md:hidden p-2 rounded-lg bg-hs-elevated/80 border border-hs-border-primary text-hs-text-secondary hover:text-hs-text-primary transition-colors"
              aria-label="Open mobile menu"
            >
              <Menu className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
