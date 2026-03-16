import type { EmailOtpType } from "@supabase/supabase-js";
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

import { getSupabasePublicConfig } from "@/lib/supabase/config";

export async function handleSupabaseAuthCallback(request: NextRequest) {
  const config = getSupabasePublicConfig();
  const next = request.nextUrl.searchParams.get("next") ?? "/onboarding";
  const redirectUrl = new URL(next, request.url);

  if (!config) {
    redirectUrl.pathname = "/sign-in";
    redirectUrl.searchParams.set("error", "missing_supabase_config");
    return NextResponse.redirect(redirectUrl);
  }

  let response = NextResponse.redirect(redirectUrl);
  const supabase = createServerClient(config.url, config.publicKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => {
          response.cookies.set(name, value, options);
        });
      },
    },
  });

  const code = request.nextUrl.searchParams.get("code");
  const tokenHash = request.nextUrl.searchParams.get("token_hash");
  const type = request.nextUrl.searchParams.get("type");

  let errorMessage: string | null = null;

  if (code) {
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    errorMessage = error?.message ?? null;
  } else if (tokenHash && type) {
    const { error } = await supabase.auth.verifyOtp({
      token_hash: tokenHash,
      type: type as EmailOtpType,
    });
    errorMessage = error?.message ?? null;
  } else {
    errorMessage = "missing_auth_params";
  }

  if (errorMessage) {
    const fallbackUrl = new URL("/sign-in", request.url);
    fallbackUrl.searchParams.set("error", errorMessage);
    return NextResponse.redirect(fallbackUrl);
  }

  return response;
}
