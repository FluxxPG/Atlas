import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function Card({
  className,
  children
}: {
  className?: string;
  children: ReactNode;
}) {
  return <div className={cn("glass rounded-[28px] p-6", className)}>{children}</div>;
}
