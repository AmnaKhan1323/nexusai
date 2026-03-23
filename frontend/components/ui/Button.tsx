import { forwardRef, ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface-900";

    const variants = {
      primary:
        "bg-gradient-to-r from-brand-600 to-violet-600 text-white shadow-lg shadow-brand-500/25 hover:shadow-xl hover:shadow-brand-500/40 hover:brightness-110 focus:ring-brand-500",
      secondary:
        "border border-gray-700 bg-surface-800/50 text-gray-300 backdrop-blur-sm hover:border-gray-600 hover:bg-surface-700/50 hover:text-white focus:ring-gray-500",
      ghost:
        "text-gray-400 hover:bg-surface-800 hover:text-gray-200 focus:ring-gray-500",
      danger:
        "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 focus:ring-red-500",
    };

    const sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-6 py-3 text-sm",
      lg: "px-8 py-4 text-base",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
