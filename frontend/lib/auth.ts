import { redirect } from "next/navigation";

import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { UserOnboardingProfile, ViewerState } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function getViewerState(): Promise<ViewerState> {
  const supabase = await createSupabaseServerClient();

  if (!supabase) {
    return {
      isAuthenticated: false,
      email: null,
      hasSupabaseAuth: false,
      onboarding: null,
    };
  }

  const { data: claimsData } = await supabase.auth.getClaims();

  const emailFromClaims =
    claimsData && typeof claimsData.claims?.email === "string" ? claimsData.claims.email : null;
  let email = emailFromClaims;

  if (!email) {
    const {
      data: { user },
    } = await supabase.auth.getUser();
    email = user?.email ?? null;
  }

  const onboarding = email ? await getOnboardingState(email) : null;

  return {
    isAuthenticated: Boolean(email),
    email,
    hasSupabaseAuth: true,
    onboarding,
  };
}

export async function requireAuthenticatedViewer() {
  const viewer = await getViewerState();
  if (!viewer.isAuthenticated) {
    redirect("/sign-in");
  }
  return viewer;
}

export async function requireOnboardedViewer() {
  const viewer = await requireAuthenticatedViewer();
  if (!viewer.onboarding) {
    redirect("/onboarding");
  }
  return viewer;
}

async function getOnboardingState(email: string): Promise<UserOnboardingProfile | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/me`, {
      cache: "no-store",
      headers: {
        "x-user-email": email,
      },
    });
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as {
      tracked_symbols: string[];
      alert_preference: string | null;
      onboarding_completed_at: string | null;
    };
    if (!data.onboarding_completed_at || !data.alert_preference) {
      return null;
    }
    return {
      trackedSymbols: data.tracked_symbols,
      alertPreference: data.alert_preference as UserOnboardingProfile["alertPreference"],
      completedAt: data.onboarding_completed_at,
    };
  } catch {
    return null;
  }
}
