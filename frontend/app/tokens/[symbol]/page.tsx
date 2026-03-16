import { redirect } from "next/navigation";

import { getViewerState } from "@/lib/auth";

export default async function TokenPage({
  params,
}: {
  params: Promise<{ symbol: string }>;
}) {
  const { symbol } = await params;
  const viewer = await getViewerState();
  redirect(viewer.isAuthenticated ? `/app?symbol=${symbol.toUpperCase()}` : "/sign-in");
}
