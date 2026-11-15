import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Search, CornerDownLeft, Sparkles, X } from "lucide-react";
import { NAV_ITEMS } from "./navData";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Filter items based on query
  const filteredItems = NAV_ITEMS.filter((item) => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return (
      item.title.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q) ||
      item.badge?.toLowerCase().includes(q)
    );
  });

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Global keydown listeners for ArrowUp, ArrowDown, Enter, Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % (filteredItems.length || 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredItems.length) % (filteredItems.length || 1));
      } else if (e.key === "Enter" && filteredItems.length > 0) {
        e.preventDefault();
        const selected = filteredItems[selectedIndex];
        if (selected) {
          navigate(selected.path);
          onClose();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, filteredItems, selectedIndex, navigate, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-hs-void/80 backdrop-blur-md transition-opacity"
        onClick={onClose}
      />

      {/* Palette Modal */}
      <div className="relative w-full max-w-2xl bg-hs-graphite/95 border border-hs-border-primary rounded-2xl shadow-[0_24px_50px_rgba(0,0,0,0.8)] overflow-hidden z-10 flex flex-col backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-hs-border-primary gap-3">
          <Search className="w-5 h-5 text-hs-cyan-ion shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command or jump to an experience..."
            className="w-full bg-transparent text-hs-text-primary placeholder:text-hs-text-disabled text-sm font-sans focus:outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 text-hs-text-muted hover:text-hs-text-primary rounded-md hover:bg-hs-elevated transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filteredItems.length === 0 ? (
            <div className="py-12 text-center text-sm text-hs-text-muted">
              No matching environments or tools found for "{query}".
            </div>
          ) : (
            filteredItems.map((item, index) => {
              const Icon = item.icon;
              const isSelected = index === selectedIndex;

              return (
                <div
                  key={item.id}
                  onClick={() => {
                    navigate(item.path);
                    onClose();
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? "bg-hs-elevated text-hs-text-primary border border-hs-cyan-ion/40 shadow-sm"
                      : "text-hs-text-secondary hover:bg-hs-elevated/50 border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`p-2 rounded-lg ${
                        isSelected
                          ? "bg-hs-cyan-deep/30 text-hs-cyan-bright"
                          : "bg-hs-elevated text-hs-text-muted"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-hs-text-primary truncate">
                          {item.title}
                        </span>
                        <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-hs-void text-hs-text-muted border border-hs-border-subtle">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-xs text-hs-text-muted truncate mt-0.5">
                        {item.description}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 ml-3">
                    {item.badge && (
                      <span className="hidden sm:inline-block text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-hs-cyan-deep/20 text-hs-cyan-bright border border-hs-cyan-ion/25">
                        {item.badge}
                      </span>
                    )}
                    <div
                      className={`p-1 rounded text-hs-text-muted ${
                        isSelected ? "text-hs-cyan-bright" : "opacity-0"
                      }`}
                    >
                      <CornerDownLeft className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Palette Footer */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-hs-void/70 border-t border-hs-border-primary text-[11px] text-hs-text-muted font-mono">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-hs-elevated border border-hs-border-primary rounded text-[10px]">
                ↑
              </kbd>
              <kbd className="px-1.5 py-0.5 bg-hs-elevated border border-hs-border-primary rounded text-[10px]">
                ↓
              </kbd>
              <span>to navigate</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-hs-elevated border border-hs-border-primary rounded text-[10px]">
                ↵
              </kbd>
              <span>to select</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-hs-elevated border border-hs-border-primary rounded text-[10px]">
                ESC
              </kbd>
              <span>to close</span>
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 text-hs-cyan-bright">
            <Sparkles className="w-3 h-3 text-hs-cyan-ion" />
            <span>HeatSense Phase 3.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};
