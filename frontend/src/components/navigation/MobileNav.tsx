import React, { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { X, Search, ChevronRight } from "lucide-react";
import { NAV_GROUPS } from "./navData";

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenCommandPalette: () => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({
  isOpen,
  onClose,
  onOpenCommandPalette,
}) => {
  const location = useLocation();

  // Close when location changes
  useEffect(() => {
    onClose();
  }, [location.pathname, onClose]);

  // Lock body scroll when mobile nav is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex flex-col bg-hs-void/95 backdrop-blur-xl animate-in fade-in duration-200">
      {/* Top Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-hs-border-primary">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-hs-cyan-ion shadow-[0_0_8px_rgba(99,221,242,0.8)]" />
          <span className="font-mono font-bold tracking-widest text-sm text-hs-text-primary">
            HEATSENSE
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-2 text-hs-text-muted hover:text-hs-text-primary rounded-lg bg-hs-elevated/50 border border-hs-border-subtle"
          aria-label="Close navigation"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Quick Search Button */}
      <div className="p-4 border-b border-hs-border-primary/50">
        <button
          onClick={() => {
            onClose();
            onOpenCommandPalette();
          }}
          className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-hs-graphite border border-hs-border-primary text-hs-text-muted text-sm font-sans"
        >
          <div className="flex items-center gap-2.5">
            <Search className="w-4 h-4 text-hs-cyan-ion" />
            <span>Search environments...</span>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hs-elevated text-hs-text-muted border border-hs-border-subtle">
            ⌘K
          </span>
        </button>
      </div>

      {/* Navigation Groups List */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.name} className="space-y-2">
            <div className="px-2">
              <h3 className="text-[11px] font-mono uppercase tracking-wider text-hs-cyan-bright font-semibold">
                {group.name}
              </h3>
              <p className="text-[11px] text-hs-text-muted truncate">
                {group.description}
              </p>
            </div>

            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <Link
                    key={item.id}
                    to={item.path}
                    className={`flex items-center justify-between p-3 rounded-xl transition-all ${
                      isActive
                        ? "bg-hs-elevated text-hs-cyan-bright border border-hs-cyan-ion/40 shadow-sm"
                        : "text-hs-text-secondary hover:bg-hs-elevated/50 border border-transparent"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className={`p-2 rounded-lg ${
                          isActive
                            ? "bg-hs-cyan-deep/40 text-hs-cyan-bright"
                            : "bg-hs-elevated text-hs-text-muted"
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="font-medium text-sm text-hs-text-primary truncate">
                          {item.title}
                        </span>
                        <span className="text-[11px] text-hs-text-muted truncate mt-0.5">
                          {item.description}
                        </span>
                      </div>
                    </div>

                    <ChevronRight className="w-4 h-4 text-hs-text-muted shrink-0 ml-2" />
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Mobile Footer Status */}
      <div className="p-4 border-t border-hs-border-primary bg-hs-void flex items-center justify-between text-xs font-mono text-hs-text-muted">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-hs-mint-signal" />
          <span>FIRMWARE SAFETY ACTIVE</span>
        </div>
        <span className="text-[10px] text-hs-text-muted/60">ADVISORY TWIN</span>
      </div>
    </div>
  );
};
