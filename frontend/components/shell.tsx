import Link from "next/link";
import type { Route } from "next";
import type { ReactNode } from "react";

const nav = [
  { href: "/watchlist", label: "Watchtower" },
  { href: "/signals", label: "Signals" },
  { href: "/my-edge", label: "My Edge" },
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;

export function Shell({
  title,
  eyebrow,
  description,
  children,
}: {
  title: string;
  eyebrow: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <main className="grain min-h-screen px-6 py-8 md:px-10">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col gap-6 rounded-[2rem] border border-border/70 bg-white/70 p-6 backdrop-blur md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.3em] text-primary/80">
              {eyebrow}
            </p>
            <h1 className="text-4xl font-black tracking-tight">{title}</h1>
            <p className="mt-3 max-w-2xl text-sm text-foreground/72">
              {description ??
                "Scoutkat scans divergence between X attention, Hyperliquid structure, and perp positioning."}
            </p>
          </div>
          <nav className="flex flex-wrap gap-2">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full border border-border/70 px-4 py-2 text-sm font-medium text-foreground/80 transition hover:bg-white"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        {children}
      </div>
    </main>
  );
}
