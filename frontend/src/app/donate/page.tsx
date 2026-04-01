"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getDonationPreferences,
  updateDonationPreferences,
  listMyDonations,
  type Donation,
  type DonationPreferences,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Navbar from "@/components/Navbar";

const SUGGESTED_AMOUNTS = [5, 10, 15, 25];

export default function DonatePage() {
  const router = useRouter();
  const { user, token, loading } = useAuth();
  const [prefs, setPrefs] = useState<DonationPreferences | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Preferences form
  const [autoEnabled, setAutoEnabled] = useState(false);
  const [donationType, setDonationType] = useState<"fixed" | "distance_based">("fixed");
  const [fixedAmount, setFixedAmount] = useState("10");
  const [multiplier, setMultiplier] = useState("0.50");

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (!token) return;
    const loadData = async () => {
      setDataLoading(true);
      try {
        const [prefsData, donationsData] = await Promise.all([
          getDonationPreferences(token),
          listMyDonations(token),
        ]);
        setPrefs(prefsData);
        setDonations(donationsData);

        // Seed form
        setAutoEnabled(prefsData.auto_donation_enabled);
        setDonationType(prefsData.auto_donation_type);
        if (prefsData.auto_donation_amount) {
          setFixedAmount(String(prefsData.auto_donation_amount));
        }
        if (prefsData.auto_donation_multiplier) {
          setMultiplier(String(prefsData.auto_donation_multiplier));
        }
      } catch (err) {
        console.warn("Could not load donation data", err);
      } finally {
        setDataLoading(false);
      }
    };
    void loadData();
  }, [token]);

  const handleSavePrefs = async () => {
    if (!token) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await updateDonationPreferences(token, {
        auto_donation_enabled: autoEnabled,
        auto_donation_type: donationType,
        auto_donation_amount: donationType === "fixed" ? Number(fixedAmount) : null,
        auto_donation_multiplier: donationType === "distance_based" ? Number(multiplier) : null,
      });
      setPrefs(updated);
      setMessage("Donation preferences saved.");
    } catch (err) {
      setError((err as Error).message || "Unable to save preferences.");
    } finally {
      setSaving(false);
    }
  };

  const totalDonated = donations
    .filter((d) => d.stripe_status === "succeeded")
    .reduce((sum, d) => sum + d.amount, 0);

  if (loading || !user) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <p className="text-sm text-slate-300">Loading...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="mx-auto max-w-2xl px-4 py-8 space-y-8">
        <header className="space-y-2">
          <p className="text-xs text-slate-400">Support</p>
          <h1 className="text-2xl font-semibold tracking-tight">Donations</h1>
          <p className="text-sm text-slate-400">
            Rides are always free. Voluntary donations help cover gas and vehicle expenses for our volunteer drivers.
            Every donation is processed securely through Stripe.
          </p>
        </header>

        {error && (
          <div className="rounded-md bg-red-900/30 border border-red-700 px-3 py-2 text-xs text-red-200" role="alert">
            {error}
          </div>
        )}
        {message && (
          <div className="rounded-md bg-emerald-900/30 border border-emerald-700 px-3 py-2 text-xs text-emerald-200">
            {message}
          </div>
        )}

        {/* Summary card */}
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 text-center">
            <p className="text-3xl font-bold text-emerald-400">${totalDonated.toFixed(2)}</p>
            <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Total given</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 text-center">
            <p className="text-3xl font-bold text-slate-100">
              {donations.filter((d) => d.stripe_status === "succeeded").length}
            </p>
            <p className="text-[10px] text-slate-400 uppercase tracking-wide mt-1">Donations made</p>
          </div>
        </div>

        {/* How it works */}
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">How donations work</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-900/40 text-emerald-400 text-sm font-bold">1</div>
              <h3 className="text-xs font-semibold text-slate-200">Complete a ride</h3>
              <p className="text-[11px] text-slate-400">
                After your ride is marked complete, you&apos;ll be prompted to leave a review.
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-900/40 text-emerald-400 text-sm font-bold">2</div>
              <h3 className="text-xs font-semibold text-slate-200">Choose an amount</h3>
              <p className="text-[11px] text-slate-400">
                Pick a suggested amount or enter your own. Or set up automatic donations below.
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-900/40 text-emerald-400 text-sm font-bold">3</div>
              <h3 className="text-xs font-semibold text-slate-200">Processed securely</h3>
              <p className="text-[11px] text-slate-400">
                Payments are handled by Stripe. Drivers never set prices — this is purely voluntary.
              </p>
            </div>
          </div>
        </section>

        {/* Auto-donation preferences */}
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">Automatic Donations</h2>
            <button
              type="button"
              onClick={() => setAutoEnabled(!autoEnabled)}
              className={`flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full p-1 transition-colors ${
                autoEnabled ? "bg-emerald-500" : "bg-slate-600"
              }`}
              aria-pressed={autoEnabled}
            >
              <div
                className={`h-4 w-4 rounded-full bg-white shadow-sm transition-transform ${
                  autoEnabled ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          <p className="text-xs text-slate-400">
            {autoEnabled
              ? "A donation will be automatically created after each completed ride."
              : "When enabled, you'll be prompted to donate after each ride without having to manually enter amounts."}
          </p>

          {autoEnabled && (
            <div className="space-y-4 border-t border-slate-800 pt-4">
              {/* Donation type toggle */}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setDonationType("fixed")}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium transition-colors ${
                    donationType === "fixed"
                      ? "border-emerald-600 bg-emerald-900/20 text-emerald-300"
                      : "border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  Fixed Amount
                </button>
                <button
                  type="button"
                  onClick={() => setDonationType("distance_based")}
                  className={`flex-1 rounded-md border px-3 py-2 text-xs font-medium transition-colors ${
                    donationType === "distance_based"
                      ? "border-emerald-600 bg-emerald-900/20 text-emerald-300"
                      : "border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  Per-Mile
                </button>
              </div>

              {donationType === "fixed" ? (
                <div className="space-y-2">
                  <label className="block text-xs text-slate-300">Donation amount per ride</label>
                  <div className="flex gap-2">
                    {SUGGESTED_AMOUNTS.map((amt) => (
                      <button
                        key={amt}
                        type="button"
                        onClick={() => setFixedAmount(String(amt))}
                        className={`flex-1 rounded-md border px-2 py-2 text-sm font-semibold transition-colors ${
                          fixedAmount === String(amt)
                            ? "border-emerald-500 bg-emerald-900/30 text-emerald-300"
                            : "border-slate-700 text-slate-300 hover:border-slate-500"
                        }`}
                      >
                        ${amt}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-400">$</span>
                    <input
                      type="number"
                      min="1"
                      max="500"
                      step="1"
                      value={fixedAmount}
                      onChange={(e) => setFixedAmount(e.target.value)}
                      className="w-24 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    />
                    <span className="text-xs text-slate-500">per ride</span>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <label className="block text-xs text-slate-300">Base: $5.00 + per-mile rate</label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-400">$</span>
                    <input
                      type="number"
                      min="0.10"
                      max="5.00"
                      step="0.10"
                      value={multiplier}
                      onChange={(e) => setMultiplier(e.target.value)}
                      className="w-24 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    />
                    <span className="text-xs text-slate-500">per mile</span>
                  </div>
                  <p className="text-[10px] text-slate-500">
                    Example: a 10-mile ride = $5.00 + (10 × ${Number(multiplier).toFixed(2)}) = ${(5 + 10 * Number(multiplier)).toFixed(2)}
                  </p>
                </div>
              )}

              <button
                type="button"
                onClick={handleSavePrefs}
                disabled={saving}
                className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-400 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
              >
                {saving ? "Saving..." : "Save Preferences"}
              </button>
            </div>
          )}

          {!autoEnabled && prefs?.auto_donation_enabled && (
            <button
              type="button"
              onClick={handleSavePrefs}
              disabled={saving}
              className="rounded-md border border-slate-700 px-4 py-2 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-60 transition-colors"
            >
              {saving ? "Saving..." : "Disable Auto-Donation"}
            </button>
          )}
        </section>

        {/* Donation history */}
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Donation History</h2>

          {dataLoading ? (
            <p className="text-xs text-slate-400 py-4 text-center">Loading...</p>
          ) : donations.length === 0 ? (
            <div className="rounded-md border border-dashed border-slate-700 p-6 text-center">
              <p className="text-sm text-slate-400">No donations yet</p>
              <p className="text-xs text-slate-500 mt-1">
                After completing a ride, you&apos;ll be able to make a voluntary donation to support your driver.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/50 text-slate-400">
                  <tr>
                    <th className="px-3 py-2 font-medium">Date</th>
                    <th className="px-3 py-2 font-medium">Ride</th>
                    <th className="px-3 py-2 font-medium text-right">Amount</th>
                    <th className="px-3 py-2 font-medium text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {donations.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-800/30">
                      <td className="px-3 py-3">{new Date(d.created_at).toLocaleDateString()}</td>
                      <td className="px-3 py-3">#{d.ride_id}</td>
                      <td className="px-3 py-3 text-right font-semibold text-slate-200">
                        ${d.amount.toFixed(2)}
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide ${
                            d.stripe_status === "succeeded"
                              ? "bg-emerald-900/50 text-emerald-400"
                              : d.stripe_status === "failed"
                              ? "bg-red-900/50 text-red-400"
                              : "bg-amber-900/50 text-amber-400"
                          }`}
                        >
                          {d.stripe_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Bottom message */}
        <div className="text-center py-4">
          <p className="text-xs text-slate-500">
            🙏 Thank you for supporting our volunteer drivers. Every donation helps keep this ministry going.
          </p>
        </div>
      </div>
    </main>
  );
}
