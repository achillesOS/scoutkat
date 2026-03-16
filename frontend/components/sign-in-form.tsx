"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export function SignInForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const supabase = createSupabaseBrowserClient();

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!supabase) {
      setMessage("Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to enable magic link sign-in.");
      return;
    }

    setPending(true);
    setMessage(null);
    const redirectTo = `${window.location.origin}/auth/callback?next=/onboarding`;
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: redirectTo },
    });

    if (error) {
      setMessage(error.message);
    } else {
      setMessage("Magic link sent. Open it to continue into Scoutkat onboarding.");
    }
    setPending(false);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="text-sm font-semibold text-foreground/70">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-2 w-full rounded-2xl border border-border/70 bg-white px-4 py-3 text-sm outline-none transition focus:border-primary"
          placeholder="you@domain.com"
        />
      </div>
      <Button type="submit" className="w-full" disabled={pending}>
        {pending ? "Sending magic link..." : "Send magic link"}
      </Button>
      {message ? <p className="text-sm text-foreground/62">{message}</p> : null}
    </form>
  );
}
