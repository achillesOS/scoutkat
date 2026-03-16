import { redirect } from "next/navigation";

import { OnboardingFlow } from "@/components/onboarding-flow";
import { Shell } from "@/components/shell";
import { requireAuthenticatedViewer } from "@/lib/auth";
import { getTokens } from "@/lib/api";

export default async function OnboardingPage() {
  const viewer = await requireAuthenticatedViewer();
  if (viewer.onboarding) {
    redirect("/watchlist");
  }
  const tokens = await getTokens();

  return (
    <Shell
      title="Onboarding"
      eyebrow="Set up Scoutkat"
      description="Choose tracked assets and alert priorities so Scoutkat can build a personal watchlist around your market focus."
    >
      <section className="mx-auto max-w-4xl">
        <OnboardingFlow tokens={tokens} />
      </section>
    </Shell>
  );
}
