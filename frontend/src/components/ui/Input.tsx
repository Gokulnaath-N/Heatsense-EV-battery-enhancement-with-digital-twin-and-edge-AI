import React, { forwardRef } from "react";
import { X } from "lucide-react";

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
  label?: string;
  error?: string;
  isMono?: boolean;
  leftIcon?: React.ReactNode;
  rightAction?: React.ReactNode;
  onClear?: () => void;
  sizeVariant?: "sm" | "md" | "lg";
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      isMono = false,
      leftIcon,
      rightAction,
      onClear,
      sizeVariant = "md",
      className = "",
      value,
      disabled,
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      sm: "h-8 text-xs px-2.5",
      md: "h-10 text-sm px-3",
      lg: "h-12 text-base px-4",
    };

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label className="text-xs font-medium uppercase tracking-wider text-hs-text-muted flex items-center justify-between">
            <span>{label}</span>
            {error && (
              <span className="text-[11px] text-hs-coral-alert normal-case font-normal">
                {error}
              </span>
            )}
          </label>
        )}

        <div className="relative flex items-center w-full">
          {leftIcon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-hs-text-muted">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            value={value}
            disabled={disabled}
            className={`
              w-full rounded-lg bg-hs-graphite/90 text-hs-text-primary placeholder:text-hs-text-disabled
              border transition-all duration-150
              ${error ? "border-hs-coral-alert/70 focus:border-hs-coral-alert" : "border-hs-border-primary hover:border-hs-border-subtle focus:border-hs-cyan-bright"}
              focus:outline-none focus:ring-1 focus:ring-hs-cyan-bright/40
              disabled:opacity-40 disabled:cursor-not-allowed
              ${isMono ? "font-mono tracking-tight" : "font-sans"}
              ${sizeClasses[sizeVariant]}
              ${leftIcon ? "pl-9" : ""}
              ${onClear && value ? "pr-16" : rightAction ? "pr-10" : ""}
              ${className}
            `}
            {...props}
          />

          <div className="absolute right-2.5 flex items-center gap-1">
            {onClear && value && !disabled && (
              <button
                type="button"
                onClick={onClear}
                className="p-1 text-hs-text-muted hover:text-hs-text-primary transition-colors rounded-sm hover:bg-hs-elevated"
                title="Clear input"
                tabIndex={-1}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
            {rightAction && <div className="flex items-center">{rightAction}</div>}
          </div>
        </div>
      </div>
    );
  }
);

Input.displayName = "Input";

