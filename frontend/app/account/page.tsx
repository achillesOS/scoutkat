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
      eyebrow="Session and access"
      description="Manage your Scoutkat session, alert profile, and the future API layer your own agent will use."
    >
      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="border border-white/12 bg-white/[0.02]">
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/34">Session</p>
          <p className="display mt-4 text-3xl text-white">Access profile</p>
          <div className="mt-6 space-y-3 text-sm leading-7 text-white/60">
            <p>Signed in as {viewer.email ?? "Unknown email"}.</p>
            <p>
              Auth method: {viewer.hasSupabaseAuth ? "Supabase magic link" : "Supabase auth not configured"}.
            </p>
          </div>
          <form action={signOutAction} className="mt-8">
            <Button type="submit" variant="secondary">
              Sign out
            </Button>
          </form>
        </Card>

        <Card className="border border-white/12 bg-white/[0.02]">
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/34">Workspace profile</p>
          <p className="display mt-4 text-3xl text-white">Current preferences</p>
          {viewer.onboarding ? (
            <div className="mt-6 space-y-3 text-sm leading-7 text-white/60">
              <p>Alert preference: {alertPreferenceLabels[viewer.onboarding.alertPreference]}.</p>
              <p>Tracked assets: {viewer.onboarding.trackedSymbols.join(", ")}.</p>
            </div>
          ) : (
            <p className="mt-6 text-sm leading-7 text-white/60">You have not completed onboarding yet.</p>
          )}
        </Card>

        <Card className="border border-white/12 bg-white/[0.02] lg:col-span-2">
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/34">Agent access</p>
          <p className="display mt-4 text-3xl text-white">API guide entry point</p>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div className="border border-white/12 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-white/42">Status</p>
              <p className="mt-3 text-sm leading-7 text-white/60">
                API keys are planned next so users can let their own agent read watchlists and signal context directly.
              </p>
            </div>
            <div className="border border-white/12 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-white/42">Planned scope</p>
              <p className="mt-3 text-sm leading-7 text-white/60">
                Watchlist state, selected asset context, and signal summaries will be exposed through stable JSON endpoints.
              </p>
            </div>
            <div className="border border-white/12 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-white/42">Intent</p>
              <p className="mt-3 text-sm leading-7 text-white/60">
                The UI stays for people. The API exists so each user&apos;s own agent can consume the same source of truth.
              </p>
            </div>
          </div>
        </Card>
      </section>
    </Shell>
  );
}
