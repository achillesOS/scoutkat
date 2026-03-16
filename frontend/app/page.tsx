import Link from "next/link";

import { WatchtowerScreen } from "@/components/watchtower-screen";
import { Button } from "@/components/ui/button";
import { getViewerState } from "@/lib/auth";
import { getTokens, getWatchtowerOverview } from "@/lib/api";
import { emptyWatchtowerOverview } from "@/lib/empty-state";

export default async function HomePage() {
  const viewer = await getViewerState();
  const [overview, tokens] = await Promise.all([getWatchtowerOverview(), getTokens()]);

  return (
    <WatchtowerScreen
      title="Scoutkat"
      eyebrow="Scoutkat / 哨鼬"
      description="Spot divergence between X attention, Hyperliquid structure, and perp positioning before the crowd catches up."
      overview={overview ?? emptyWatchtowerOverview}
      universeTokens={tokens}
      listTitle="Live signal board"
      listBody="Public Scoutkat board for major Hyperliquid names, ranked by the latest divergence state and signal quality."
      actions={
        <>
          <Button asChild>
            <Link href={viewer.isAuthenticated ? "/watchlist" : "/sign-in"}>
              {viewer.isAuthenticated ? "Open my watchlist" : "Get started"}
            </Link>
          </Button>
          <Button asChild variant="ghost">
            <Link href="/signals">Browse signals</Link>
          </Button>
        </>
      }
    />
  );
}
