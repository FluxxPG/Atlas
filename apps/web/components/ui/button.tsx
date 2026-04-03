import * as React from "react";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean;
  variant?: "default" | "ghost" | "outline";
};

export function Button({
  className,
  variant = "default",
  asChild,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition duration-300",
        variant === "default" &&
          "bg-gradient-to-r from-glow to-accent text-ink shadow-[0_0_30px_rgba(79,209,197,0.35)] hover:scale-[1.02]",
        variant === "ghost" && "text-white/80 hover:bg-white/5 hover:text-white",
        variant === "outline" && "border border-white/15 bg-white/5 text-white hover:bg-white/10",
        className
      )}
      {...props}
    />
  );
}

