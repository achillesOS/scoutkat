import Link from "next/link";

import { WatchtowerScreen } from "@/components/watchtower-screen";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getViewerState } from "@/lib/auth";
import { getTokens, getWatchtowerOverview } from "@/lib/api";
import { emptyWatchtowerOverview } from "@/lib/empty-state";

export default async function WatchlistPage() {
  const viewer = await getViewerState();

  if (!viewer.isAuthenticated || !viewer.onboarding || !viewer.email) {
    return (
      <WatchtowerScreen
        title="Watchlist"
        eyebrow="Scoutkat / 哨鼬"
        description="Save the major names you care about and let Scoutkat prioritize signals, social refresh, and Telegram alerts around them."
        overview={emptyWatchtowerOverview}
        universeTokens={await getTokens()}
        listTitle="Your watchlist is waiting"
        listBody="Sign in with a magic link to create a personal watchlist and keep divergence tracking tied to your session."
        actions={
          <Button asChild>
            <Link href="/sign-in">Sign in with magic link</Link>
          </Button>
        }
      />
    );
  }

  const [overview, tokens] = await Promise.all([
    getWatchtowerOverview(undefined, viewer.email),
    getTokens(),
  ]);

  return (
    <WatchtowerScreen
      title="Watchlist"
      eyebrow="Scoutkat / 哨鼬"
      description="Your personal board for the assets you want Scoutkat to prioritize for social refresh and signal delivery."
      overview={overview ?? emptyWatchtowerOverview}
      universeTokens={tokens}
      listTitle="Tracked assets"
      listBody="These assets are ranked by current divergence and recent state change, using your live watchlist."
      actions={
        <Button asChild variant="ghost">
          <Link href="/account">Manage account</Link>
        </Button>
      }
    />
  );
}
