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
    <main className="grain min-h-screen bg-background px-4 py-4 md:px-6">
      <div className="mx-auto max-w-[1500px]">
        <header className="grid border border-white/12 md:grid-cols-[380px_minmax(0,1fr)_220px]">
          <Link
            href={viewer.isAuthenticated && viewer.onboarding ? "/app" : "/"}
            className="flex min-h-[72px] items-center border-b border-white/12 px-5 md:border-b-0 md:border-r"
          >
            <div>
              <p className="display text-[2rem] font-semibold leading-none text-white">Scoutkat</p>
              <p className="mt-2 text-[10px] uppercase tracking-[0.34em] text-white/42">Signal system v1</p>
            </div>
          </Link>

          <div className="flex min-h-[72px] items-center justify-between gap-4 border-b border-white/12 px-5 md:border-b-0 md:px-8">
            <div>
              <p className="text-[10px] uppercase tracking-[0.34em] text-white/35">{eyebrow}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-white/80">{title}</p>
            </div>
            <nav className="flex flex-wrap justify-end gap-2">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="border border-transparent px-3 py-2 text-[10px] uppercase tracking-[0.26em] text-white/55 transition hover:border-white/16 hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex min-h-[72px] items-center justify-end px-5">
            {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
          </div>
        </header>

        <section className="border-x border-b border-white/12 px-5 py-8 md:px-8 md:py-10">
          <div className="max-w-3xl">
            <p className="text-[10px] uppercase tracking-[0.34em] text-white/32">{eyebrow}</p>
            <h1 className="display mt-4 text-4xl leading-none text-white md:text-6xl">{title}</h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-white/62">
              {description ??
                "Scoutkat compares social attention, structure, and positioning to frame live crypto setups."}
            </p>
          </div>
        </section>

        <div className="border-x border-b border-white/12 p-5 md:p-8">{children}</div>
      </div>
    </main>
  );
}

const publicNav = [
  { href: "/", label: "Home" },
  { href: "/sign-in", label: "Sign in" },
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;

const privateNav = [
  { href: "/app", label: "Workspace" },
  { href: "/account", label: "Account" },
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;
