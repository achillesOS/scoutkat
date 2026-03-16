import * as React from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "hairline bg-card/96 p-5 backdrop-blur-sm",
        className,
      )}
      {...props}
    />
  );
}
