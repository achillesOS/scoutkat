import { redirect } from "next/navigation";

import { OnboardingFlow } from "@/components/onboarding-flow";
import { Shell } from "@/components/shell";
import { requireAuthenticatedViewer } from "@/lib/auth";
import { fallbackWorkspaceTokens } from "@/lib/fallback-workspace";
import { getTokens } from "@/lib/api";

export default async function OnboardingPage() {
  const viewer = await requireAuthenticatedViewer();
  if (viewer.onboarding) {
    redirect("/app");
  }
  const liveTokens = await getTokens();
  const tokens = liveTokens.length > 0 ? liveTokens : fallbackWorkspaceTokens;

  return (
    <Shell
      title="Onboarding"
      eyebrow="Set up Scoutkat"
      description={
        liveTokens.length > 0
          ? "Choose a starting watchlist and an alert posture. After this, Scoutkat drops you straight into the private workspace."
          : "Live asset discovery is temporarily unavailable, so Scoutkat is offering a default starter set to get you into the workspace."
      }
    >
      <section className="mx-auto max-w-4xl">
        <OnboardingFlow tokens={tokens} />
      </section>
    </Shell>
  );
}
