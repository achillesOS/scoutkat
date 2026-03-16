import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-none border px-4 py-2.5 text-xs font-medium uppercase tracking-[0.22em] transition-colors",
  {
    variants: {
      variant: {
        default: "border-white bg-white text-black hover:bg-transparent hover:text-white",
        secondary: "border-white/18 bg-transparent text-white hover:border-white hover:bg-white hover:text-black",
        ghost: "border-white/12 bg-transparent text-white/74 hover:border-white/28 hover:bg-white/[0.04] hover:text-white",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export function Button({
  className,
  variant,
  asChild = false,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ variant }), className)} {...props} />;
}
