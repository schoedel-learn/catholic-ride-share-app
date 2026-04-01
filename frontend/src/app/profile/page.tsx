"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import {
  deleteProfilePhoto,
  getDonationPreferences,
  listParishes,
  updateDonationPreferences,
  updateCurrentUser,
  uploadProfilePhoto,
  type Parish,
  type DonationPreferences,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Navbar from "@/components/Navbar";

export default function ProfilePage() {
  const router = useRouter();
  const { user, token, loading, setUser, logout } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [parishId, setParishId] = useState("");
  const [saving, setSaving] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [donationPrefs, setDonationPrefs] = useState<DonationPreferences | null>(null);
  const [donationPrefsLoading, setDonationPrefsLoading] = useState(false);
  const [donationPrefsSaving, setDonationPrefsSaving] = useState(false);
  const [donationPrefsError, setDonationPrefsError] = useState<string | null>(null);
  const [donationPrefsMessage, setDonationPrefsMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      setFirstName(user.first_name);
      setLastName(user.last_name);
      setPhone(user.phone ?? "");
      setParishId(user.parish_id ? String(user.parish_id) : "");
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (!token) return;
    const loadPrefs = async () => {
      setDonationPrefsLoading(true);
      setDonationPrefsError(null);
      try {
        const prefs = await getDonationPreferences(token);
        setDonationPrefs(prefs);
      } catch (err) {
        setDonationPrefsError((err as Error).message || "Unable to load donation preferences");
      } finally {
        setDonationPrefsLoading(false);
      }
    };
    void loadPrefs();
  }, [token]);

  useEffect(() => {
    const fetchParishes = async () => {
      try {
        const data = await listParishes();
        setParishes(data);
      } catch (err) {
        console.warn("Unable to load parishes", err);
      }
    };

    void fetchParishes();
  }, []);

  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await updateCurrentUser(token, {
        first_name: firstName,
        last_name: lastName,
        phone,
        parish_id: parishId ? Number(parishId) : undefined,
      });
      setUser(updated);
      setMessage("Profile updated.");
    } catch (err) {
      setError((err as Error).message || "Unable to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handlePhotoChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!token) return;
    const file = event.target.files?.[0];
    if (!file) return;
    setPhotoLoading(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await uploadProfilePhoto(token, file);
      setUser(updated);
      setMessage("Profile photo updated.");
    } catch (err) {
      setError((err as Error).message || "Unable to upload photo");
    } finally {
      setPhotoLoading(false);
    }
  };

  const handleRemovePhoto = async () => {
    if (!token) return;
    setPhotoLoading(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await deleteProfilePhoto(token);
      setUser(updated);
      setMessage("Profile photo removed.");
    } catch (err) {
      setError((err as Error).message || "Unable to remove photo");
    } finally {
      setPhotoLoading(false);
    }
  };

  const handleSaveDonationPrefs = async (e: FormEvent) => {
    e.preventDefault();
    if (!token || !donationPrefs) return;
    setDonationPrefsSaving(true);
    setDonationPrefsError(null);
    setDonationPrefsMessage(null);
    try {
      const updated = await updateDonationPreferences(token, {
        auto_donation_enabled: donationPrefs.auto_donation_enabled,
        auto_donation_type: donationPrefs.auto_donation_type,
        auto_donation_amount: donationPrefs.auto_donation_amount ?? null,
        auto_donation_multiplier: donationPrefs.auto_donation_multiplier ?? null,
      });
      setDonationPrefs(updated);
      setDonationPrefsMessage("Donation preferences updated.");
    } catch (err) {
      setDonationPrefsError((err as Error).message || "Unable to update donation preferences");
    } finally {
      setDonationPrefsSaving(false);
    }
  };

  if (loading || (!user && !error)) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <p className="text-sm text-slate-300">Loading your profile...</p>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />

      <div className="mx-auto max-w-4xl px-4 py-8 grid gap-8 md:grid-cols-[minmax(0,2fr)_minmax(0,1.2fr)]">
        <section>
          <h2 className="text-sm font-semibold text-slate-300 mb-3">
            Basic information
          </h2>
          <form onSubmit={handleSave} className="space-y-4">
            {error && (
              <div className="rounded-md bg-red-900/30 border border-red-700 px-3 py-2 text-xs text-red-200">
                {error}
              </div>
            )}
            {message && (
              <div className="rounded-md bg-emerald-900/30 border border-emerald-700 px-3 py-2 text-xs text-emerald-200">
                {message}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="first_name"
                  className="block text-xs font-medium text-slate-300"
                >
                  First name
                </label>
                <input
                  id="first_name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label
                  htmlFor="last_name"
                  className="block text-xs font-medium text-slate-300"
                >
                  Last name
                </label>
                <input
                  id="last_name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="phone"
                className="block text-xs font-medium text-slate-300"
              >
                Phone
              </label>
              <input
                id="phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label
                htmlFor="parish"
                className="block text-xs font-medium text-slate-300"
              >
                Home parish (optional)
              </label>
              <select
                id="parish"
                value={parishId}
                onChange={(e) => setParishId(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">Select parish</option>
                {parishes.map((parish) => (
                  <option key={parish.id} value={parish.id}>
                    {parish.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center justify-center rounded-md bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-slate-950 shadow-sm hover:bg-emerald-400 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
            >
              {saving ? "Saving..." : "Save changes"}
            </button>
          </form>
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-300">
            Profile photo
          </h2>
          <div className="flex items-center gap-4">
            <div className="h-20 w-20 rounded-full border border-slate-700 bg-slate-800 flex items-center justify-center overflow-hidden">
              {user.profile_photo_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={user.profile_photo_url}
                  alt="Profile"
                  className="h-full w-full object-cover"
                />
              ) : (
                <span className="text-sm text-slate-400">No photo</span>
              )}
            </div>
            <div className="flex flex-col gap-2">
              <label className="inline-flex items-center gap-2 text-xs font-medium text-emerald-300 hover:text-emerald-200 cursor-pointer">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={handlePhotoChange}
                />
                {photoLoading ? "Uploading..." : "Upload new photo"}
              </label>
              {user.profile_photo_url && (
                <button
                  type="button"
                  onClick={handleRemovePhoto}
                  disabled={photoLoading}
                  className="text-xs text-slate-400 hover:text-slate-200"
                >
                  Remove current photo
                </button>
              )}
              <p className="text-[10px] text-slate-500">
                JPEG, PNG, or WebP up to 5MB. We store a 500×500 thumbnail for
                privacy and performance.
              </p>
            </div>
          </div>
        </section>

        <section className="md:col-span-2">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">Donations</h2>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
            <p className="text-xs text-slate-400">
              Rides are always free. If you’d like to help keep the app running, you can opt into
              donating per ride.
            </p>

            {donationPrefsLoading && (
              <p className="mt-3 text-xs text-slate-400">Loading donation preferences…</p>
            )}
            {donationPrefsError && (
              <div className="mt-3 rounded-md bg-red-900/30 border border-red-700 px-3 py-2 text-xs text-red-200">
                {donationPrefsError}
              </div>
            )}
            {donationPrefsMessage && (
              <div className="mt-3 rounded-md bg-emerald-900/30 border border-emerald-700 px-3 py-2 text-xs text-emerald-200">
                {donationPrefsMessage}
              </div>
            )}

            {donationPrefs && (
              <form onSubmit={handleSaveDonationPrefs} className="mt-4 space-y-4">
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    className="mt-0.5 h-4 w-4 rounded border-slate-700 bg-slate-950 text-emerald-500 focus:ring-emerald-500"
                    checked={donationPrefs.auto_donation_enabled}
                    onChange={(e) =>
                      setDonationPrefs({
                        ...donationPrefs,
                        auto_donation_enabled: e.target.checked,
                      })
                    }
                  />
                  <span>
                    <span className="block text-sm font-medium text-slate-100">
                      Automatically prompt me to donate after each completed ride
                    </span>
                    <span className="block text-xs text-slate-400">
                      You can turn this off anytime. Your ride is never affected.
                    </span>
                  </span>
                </label>

                <fieldset className="space-y-2">
                  <legend className="text-xs font-medium text-slate-300">Donation style</legend>
                  <label className="flex items-center gap-2 text-sm text-slate-200">
                    <input
                      type="radio"
                      name="donation_type"
                      className="h-4 w-4 border-slate-700 bg-slate-950 text-emerald-500 focus:ring-emerald-500"
                      checked={donationPrefs.auto_donation_type === "fixed"}
                      onChange={() =>
                        setDonationPrefs({
                          ...donationPrefs,
                          auto_donation_type: "fixed",
                        })
                      }
                    />
                    Fixed amount per ride
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-200">
                    <input
                      type="radio"
                      name="donation_type"
                      className="h-4 w-4 border-slate-700 bg-slate-950 text-emerald-500 focus:ring-emerald-500"
                      checked={donationPrefs.auto_donation_type === "distance_based"}
                      onChange={() =>
                        setDonationPrefs({
                          ...donationPrefs,
                          auto_donation_type: "distance_based",
                        })
                      }
                    />
                    Suggested based on distance
                  </label>
                </fieldset>

                {donationPrefs.auto_donation_type === "fixed" ? (
                  <div>
                    <label
                      htmlFor="auto_donation_amount"
                      className="block text-xs font-medium text-slate-300"
                    >
                      Fixed amount (USD)
                    </label>
                    <input
                      id="auto_donation_amount"
                      type="number"
                      step="1"
                      min="1"
                      max="1000"
                      value={donationPrefs.auto_donation_amount ?? ""}
                      onChange={(e) =>
                        setDonationPrefs({
                          ...donationPrefs,
                          auto_donation_amount: e.target.value ? Number(e.target.value) : null,
                        })
                      }
                      className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                      placeholder="e.g. 10"
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label
                        htmlFor="auto_donation_multiplier"
                        className="block text-xs font-medium text-slate-300"
                      >
                        Per mile (USD)
                      </label>
                      <input
                        id="auto_donation_multiplier"
                        type="number"
                        step="0.1"
                        min="0.01"
                        max="50"
                        value={donationPrefs.auto_donation_multiplier ?? 0.5}
                        onChange={(e) =>
                          setDonationPrefs({
                            ...donationPrefs,
                            auto_donation_multiplier: Number(e.target.value),
                          })
                        }
                        className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                      />
                      <p className="mt-1 text-[10px] text-slate-500">
                        Suggested total = $5 base + (miles × per mile)
                      </p>
                    </div>
                    <div className="rounded-md border border-slate-800 bg-slate-950/40 p-3">
                      <p className="text-xs font-medium text-slate-200">Example</p>
                      <p className="mt-1 text-xs text-slate-400">
                        10 miles → ${" "}
                        {(
                          5 +
                          10 * (donationPrefs.auto_donation_multiplier ?? 0.5)
                        ).toFixed(2)}
                      </p>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={donationPrefsSaving}
                  className="inline-flex items-center justify-center rounded-md bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-slate-950 shadow-sm hover:bg-emerald-400 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"
                >
                  {donationPrefsSaving ? "Saving…" : "Save donation preferences"}
                </button>
              </form>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}


