"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getViewerState } from "@/lib/auth";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { AlertPreference } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function completeOnboarding(formData: FormData) {
  const trackedSymbols = formData
    .getAll("tracked_symbols")
    .map((value) => String(value))
    .filter(Boolean);
  const alertPreference = String(formData.get("alert_preference") || "balanced") as AlertPreference;

  if (trackedSymbols.length === 0) {
    return;
  }

  const viewer = await getViewerState();
  if (!viewer.email) {
    redirect("/sign-in");
  }

  await fetch(`${API_BASE_URL}/me/onboarding`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: viewer.email,
      tracked_symbols: trackedSymbols,
      alert_preference: alertPreference,
    }),
  });

  revalidatePath("/");
  revalidatePath("/watchlist");
  redirect("/watchlist");
}

export async function signOutAction() {
  const supabase = await createSupabaseServerClient();
  if (supabase) {
    await supabase.auth.signOut();
  }

  revalidatePath("/");
  redirect("/");
}

export async function toggleTrackedAsset(formData: FormData) {
  const viewer = await getViewerState();
  const tokenSymbol = String(formData.get("symbol") || "").toUpperCase();
  const intent = String(formData.get("intent") || "add");

  if (!viewer.isAuthenticated || !viewer.onboarding || !tokenSymbol) {
    redirect("/sign-in");
  }

  const nextTrackedSymbols = new Set(viewer.onboarding.trackedSymbols);
  if (intent === "remove") {
    nextTrackedSymbols.delete(tokenSymbol);
  } else {
    nextTrackedSymbols.add(tokenSymbol);
  }

  await fetch(`${API_BASE_URL}/me/onboarding`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: viewer.email,
      tracked_symbols: Array.from(nextTrackedSymbols),
      alert_preference: viewer.onboarding.alertPreference,
    }),
  });

  revalidatePath("/");
  revalidatePath("/watchlist");
  revalidatePath(`/tokens/${tokenSymbol}`);
}
