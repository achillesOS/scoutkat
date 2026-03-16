"use client";

import { useState } from "react";

import { completeOnboarding } from "@/app/actions";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { alertPreferenceLabels } from "@/lib/alert-preferences";
import type { AlertPreference, Token } from "@/lib/types";

const preferences: AlertPreference[] = ["early_setups", "risk_alerts", "balanced"];

export function OnboardingFlow({ tokens }: { tokens: Token[] }) {
  const [step, setStep] = useState(1);
  const [trackedSymbols, setTrackedSymbols] = useState<string[]>(tokens.slice(0, 4).map((token) => token.symbol));
  const [alertPreference, setAlertPreference] = useState<AlertPreference>("balanced");

  function toggleSymbol(symbol: string) {
    setTrackedSymbols((current) =>
      current.includes(symbol) ? current.filter((item) => item !== symbol) : [...current, symbol],
    );
  }

  return (
    <form action={completeOnboarding} className="grid gap-4">
      <Card className="border border-white/12 bg-white/[0.02] p-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-white/45">
          Step {step} of 3
        </p>

        {step === 1 ? (
          <>
            <h2 className="display mt-3 text-3xl text-white">Choose tracked assets</h2>
            <p className="mt-2 max-w-2xl text-sm text-white/60">
              Pick the assets you want Scoutkat to prioritize first.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {tokens.map((token) => {
                const selected = trackedSymbols.includes(token.symbol);
                return (
                  <button
                    key={token.id}
                    type="button"
                    onClick={() => toggleSymbol(token.symbol)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      selected
                        ? "border border-white bg-white text-black"
                        : "border border-white/16 bg-transparent text-white/70 hover:bg-white/[0.04]"
                    }`}
                  >
                    {token.symbol}
                  </button>
                );
              })}
            </div>
            <div className="mt-6 flex justify-end">
              <Button type="button" onClick={() => setStep(2)} disabled={trackedSymbols.length === 0}>
                Continue
              </Button>
            </div>
          </>
        ) : null}

        {step === 2 ? (
          <>
            <h2 className="display mt-3 text-3xl text-white">Choose alert preference</h2>
            <p className="mt-2 max-w-2xl text-sm text-white/60">
              Tell Scoutkat whether to emphasize early setups, risk alerts, or a balanced mix.
            </p>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {preferences.map((preference) => (
                <button
                  key={preference}
                  type="button"
                  onClick={() => setAlertPreference(preference)}
                  className={`rounded-[1.25rem] border p-4 text-left transition ${
                    alertPreference === preference
                      ? "border-white bg-white/[0.06]"
                      : "border-white/14 bg-transparent hover:bg-white/[0.03]"
                  }`}
                >
                  <p className="font-bold text-white">{alertPreferenceLabels[preference]}</p>
                  <p className="mt-2 text-sm text-white/58">
                    {preference === "early_setups"
                      ? "Favor early divergence before the crowd arrives."
                      : preference === "risk_alerts"
                        ? "Favor trap risk, overheating, and invalidation pressure."
                        : "Keep both setup discovery and risk monitoring in balance."}
                  </p>
                </button>
              ))}
            </div>
            <div className="mt-6 flex justify-between">
              <Button type="button" variant="ghost" onClick={() => setStep(1)}>
                Back
              </Button>
              <Button type="button" onClick={() => setStep(3)}>
                Continue
              </Button>
            </div>
          </>
        ) : null}

        {step === 3 ? (
          <>
            <h2 className="display mt-3 text-3xl text-white">Finish setup</h2>
            <p className="mt-2 max-w-2xl text-sm text-white/60">
              Scoutkat will open with your tracked assets, signal priorities, and divergence context ready.
            </p>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <div className="border border-white/12 p-4">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-white/45">
                  Tracked assets
                </p>
                <p className="mt-3 text-lg font-bold text-white">{trackedSymbols.join(", ")}</p>
              </div>
              <div className="border border-white/12 p-4">
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-white/45">
                  Alert preference
                </p>
                <p className="mt-3 text-lg font-bold text-white">{alertPreferenceLabels[alertPreference]}</p>
              </div>
            </div>
            {trackedSymbols.map((symbol) => (
              <input key={symbol} type="hidden" name="tracked_symbols" value={symbol} />
            ))}
            <input type="hidden" name="alert_preference" value={alertPreference} />
            <div className="mt-6 flex justify-between">
              <Button type="button" variant="ghost" onClick={() => setStep(2)}>
                Back
              </Button>
              <Button type="submit">Enter workspace</Button>
            </div>
          </>
        ) : null}
      </Card>
    </form>
  );
}
