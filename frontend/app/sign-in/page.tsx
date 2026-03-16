import { redirect } from "next/navigation";

import { SignInForm } from "@/components/sign-in-form";
import { Shell } from "@/components/shell";
import { Card } from "@/components/ui/card";
import { getViewerState } from "@/lib/auth";

export default async function SignInPage() {
  const viewer = await getViewerState();
  if (viewer.isAuthenticated && viewer.onboarding) {
    redirect("/app");
  }
  if (viewer.isAuthenticated) {
    redirect("/onboarding");
  }

  return (
    <Shell
      title="Sign in"
      eyebrow="Access Scoutkat"
      description="Use a magic link to unlock the private workspace, custom watchlists, Telegram alerts, and future agent access."
    >
      <section className="mx-auto max-w-xl">
        <Card className="border border-white/12 bg-white/[0.02] p-6">
          <p className="display text-3xl text-white">Initialize your session.</p>
          <p className="mt-4 text-sm leading-8 text-white/60">
            Start a 7-day Pro trial with a magic link. No password, no setup debt, just a faster path into your private Scoutkat workspace.
          </p>
          <div className="mt-6">
            <SignInForm />
          </div>
        </Card>
      </section>
    </Shell>
  );
}
