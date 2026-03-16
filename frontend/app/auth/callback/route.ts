import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { getSupabasePublicConfig } from "@/lib/supabase/config";

export async function GET(request: NextRequest) {
  const config = getSupabasePublicConfig();
  const next = request.nextUrl.searchParams.get("next") ?? "/onboarding";
  const redirectUrl = new URL(next, request.url);

  if (!config) {
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
  if (code) {
    await supabase.auth.exchangeCodeForSession(code);
  }

  return response;
}
