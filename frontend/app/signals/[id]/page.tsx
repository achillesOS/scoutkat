import { redirect } from "next/navigation";

import { getViewerState } from "@/lib/auth";

export default async function SignalDetailPage() {
  const viewer = await getViewerState();
  redirect(viewer.isAuthenticated ? "/app" : "/sign-in");
}
