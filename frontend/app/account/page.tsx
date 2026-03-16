import { signOutAction } from "@/app/actions";
import { Shell } from "@/components/shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { requireAuthenticatedViewer } from "@/lib/auth";
import { alertPreferenceLabels } from "@/lib/alert-preferences";

export default async function AccountPage() {
  const viewer = await requireAuthenticatedViewer();

  return (
    <Shell
      title="Account"
      eyebrow="User settings"
      description="Your Scoutkat session, tracked assets, and alert preference live here."
    >
      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="text-xl font-black">Session</p>
          <p className="mt-3 text-sm text-foreground/68">Signed in as {viewer.email ?? "Unknown email"}</p>
          <p className="mt-2 text-sm text-foreground/68">
            Auth provider: {viewer.hasSupabaseAuth ? "Supabase magic link" : "Supabase keys not configured"}
          </p>
          <form action={signOutAction} className="mt-5">
            <Button type="submit">Sign out</Button>
          </form>
        </Card>
        <Card>
          <p className="text-xl font-black">Scoutkat profile</p>
          {viewer.onboarding ? (
            <>
              <p className="mt-3 text-sm text-foreground/68">
                Alert preference: {alertPreferenceLabels[viewer.onboarding.alertPreference]}
              </p>
              <p className="mt-2 text-sm text-foreground/68">
                Tracked assets: {viewer.onboarding.trackedSymbols.join(", ")}
              </p>
            </>
          ) : (
            <p className="mt-3 text-sm text-foreground/68">
              You have not completed onboarding yet.
            </p>
          )}
        </Card>
      </section>
    </Shell>
  );
}
