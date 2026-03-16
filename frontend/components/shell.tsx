import Link from "next/link";
import type { Route } from "next";
import type { ReactNode } from "react";

import { getViewerState } from "@/lib/auth";

export async function Shell({
  title,
  eyebrow,
  description,
  actions,
  children,
}: {
  title: string;
  eyebrow: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const viewer = await getViewerState();
  const nav = viewer.isAuthenticated && viewer.onboarding ? privateNav : publicNav;

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
                "Scoutkat compares X attention against Hyperliquid structure and perp positioning."}
            </p>
          </div>
          <div className="flex flex-col items-start gap-3 md:items-end">
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
            {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
          </div>
        </header>
        {children}
      </div>
    </main>
  );
}

const publicNav = [
  { href: "/", label: "Home" },
  { href: "/signals", label: "Signals" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/my-edge", label: "My Edge" },
  { href: "/sign-in", label: "Sign in" },
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;

const privateNav = [
  { href: "/watchlist", label: "Watchlist" },
  { href: "/signals", label: "Signals" },
  { href: "/my-edge", label: "My Edge" },
  { href: "/account", label: "Account" },
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;
