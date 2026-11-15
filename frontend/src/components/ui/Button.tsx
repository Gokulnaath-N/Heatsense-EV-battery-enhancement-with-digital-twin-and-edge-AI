import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "coral" | "icon";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className = "",
      variant = "secondary",
      size = "md",
      isLoading = false,
      disabled = false,
      leftIcon,
      rightIcon,
      type = "button",
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-sans select-none transition-all duration-150 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hs-cyan-bright focus-visible:ring-offset-2 focus-visible:ring-offset-hs-void active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none disabled:active:scale-100";

    const sizeStyles = {
      sm: variant === "icon" ? "p-1.5" : "text-xs px-2.5 py-1.5 gap-1.5",
      md: variant === "icon" ? "p-2" : "text-sm px-3.5 py-2 gap-2",
      lg: variant === "icon" ? "p-3" : "text-base px-5 py-2.5 gap-2.5",
    };

    const variantStyles = {
      primary:
        "bg-hs-cyan-ion text-hs-void font-semibold hover:bg-hs-cyan-bright shadow-[0_0_16px_rgba(99,221,242,0.22)] border border-transparent",
      secondary:
        "bg-hs-elevated text-hs-text-primary border border-hs-border-primary hover:bg-hs-elevated-hover hover:border-hs-text-muted/40 shadow-sm",
      outline:
        "bg-transparent text-hs-text-secondary border border-hs-border-primary hover:text-hs-text-primary hover:border-hs-cyan-ion/60 hover:bg-hs-cyan-deep/10",
      ghost:
        "bg-transparent text-hs-text-secondary hover:text-hs-text-primary hover:bg-hs-elevated/60 border border-transparent",
      coral:
        "bg-hs-coral-alert/15 text-hs-coral-alert border border-hs-coral-alert/35 hover:bg-hs-coral-alert/25 hover:border-hs-coral-alert/60 shadow-[0_0_12px_rgba(255,100,124,0.15)]",
      icon:
        "bg-transparent text-hs-text-secondary hover:text-hs-text-primary hover:bg-hs-elevated/80 border border-transparent hover:border-hs-border-subtle",
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin text-current" />
        ) : (
          leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>
        )}
        {children && <span>{children}</span>}
        {!isLoading && rightIcon && (
          <span className="inline-flex shrink-0">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

