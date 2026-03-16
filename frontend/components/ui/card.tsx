import * as React from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-border/80 bg-card/90 p-5 shadow-[0_12px_40px_rgba(36,34,24,0.08)] backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}

