import { redirect } from "next/navigation";

import { SignInForm } from "@/components/sign-in-form";
import { Shell } from "@/components/shell";
import { Card } from "@/components/ui/card";
import { getViewerState } from "@/lib/auth";

export default async function SignInPage() {
  const viewer = await getViewerState();
  if (viewer.isAuthenticated && viewer.onboarding) {
    redirect("/watchlist");
  }
  if (viewer.isAuthenticated) {
    redirect("/onboarding");
  }

  return (
    <Shell
      title="Sign in"
      eyebrow="Access Scoutkat"
      description="Use a magic link to unlock your personal Scoutkat watchlist, onboarding preferences, and alert routing."
    >
      <section className="mx-auto max-w-xl">
        <Card className="rounded-[1.75rem] p-6">
          <p className="text-2xl font-black tracking-tight">Get started with Scoutkat</p>
          <p className="mt-3 text-sm leading-7 text-foreground/68">
            Sign in with email to create your own watchlist, choose alert preferences, and keep signal context tied to your session.
          </p>
          <div className="mt-6">
            <SignInForm />
          </div>
        </Card>
      </section>
    </Shell>
  );
}
