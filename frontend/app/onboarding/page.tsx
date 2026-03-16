import { redirect } from "next/navigation";

import { OnboardingFlow } from "@/components/onboarding-flow";
import { Shell } from "@/components/shell";
import { requireAuthenticatedViewer } from "@/lib/auth";
import { getTokens } from "@/lib/api";

export default async function OnboardingPage() {
  const viewer = await requireAuthenticatedViewer();
  if (viewer.onboarding) {
    redirect("/app");
  }
  const tokens = await getTokens();

  return (
    <Shell
      title="Onboarding"
      eyebrow="Set up Scoutkat"
      description="Choose a starting watchlist and an alert posture. After this, Scoutkat drops you straight into the private workspace."
    >
      <section className="mx-auto max-w-4xl">
        <OnboardingFlow tokens={tokens} />
      </section>
    </Shell>
  );
}
