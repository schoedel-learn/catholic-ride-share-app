"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  createDriverProfile,
  getDriverProfile,
  getVerificationStatus,
  type DriverProfileResponse,
  type DriverVerificationStatus,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import Navbar from "@/components/Navbar";

interface VehicleForm {
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: string;
  vehicle_color: string;
  license_plate: string;
  vehicle_capacity: string;
}

const EMPTY_FORM: VehicleForm = {
  vehicle_make: "",
  vehicle_model: "",
  vehicle_year: "",
  vehicle_color: "",
  license_plate: "",
  vehicle_capacity: "4",
};

export default function DriverProfilePage() {
  const router = useRouter();
  const { user, token, loading } = useAuth();

  const [form, setForm] = useState<VehicleForm>(EMPTY_FORM);
  const [profile, setProfile] = useState<DriverProfileResponse | null>(null);
  const [verification, setVerification] = useState<DriverVerificationStatus | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dataLoading, setDataLoading] = useState(true);

  const isDriver =
    user?.role === "driver" || user?.role === "both" || user?.role === "admin";

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    } else if (!loading && user && !isDriver) {
      router.push("/dashboard");
    }
  }, [loading, user, router, isDriver]);

  useEffect(() => {
    if (!token || !isDriver) return;

    const load = async () => {
      setDataLoading(true);
      try {
        const [prof, ver] = await Promise.allSettled([
          getDriverProfile(token),
          getVerificationStatus(token),
        ]);

        if (prof.status === "fulfilled") {
          const p = prof.value;
          setProfile(p);
          setForm({
            vehicle_make: p.vehicle_make ?? "",
            vehicle_model: p.vehicle_model ?? "",
            vehicle_year: p.vehicle_year ? String(p.vehicle_year) : "",
            vehicle_color: p.vehicle_color ?? "",
            license_plate: p.license_plate ?? "",
            vehicle_capacity: String(p.vehicle_capacity ?? 4),
          });
        }
        if (ver.status === "fulfilled") {
          setVerification(ver.value);
        }
      } finally {
        setDataLoading(false);
      }
    };

    void load();
  }, [token, isDriver]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSaving(true);
    setError(null);
    setMessage(null);

    try {
      const updated = await createDriverProfile(token, {
        vehicle_make: form.vehicle_make || undefined,
        vehicle_model: form.vehicle_model || undefined,
        vehicle_year: form.vehicle_year ? parseInt(form.vehicle_year, 10) : undefined,
        vehicle_color: form.vehicle_color || undefined,
        license_plate: form.license_plate || undefined,
        vehicle_capacity: parseInt(form.vehicle_capacity, 10),
      });
      setProfile(updated);
      setMessage("Profile saved. An admin will review your application.");
      // Reload verification status
      try {
        const ver = await getVerificationStatus(token);
        setVerification(ver);
      } catch {
        // Best effort
      }
    } catch (err) {
      setError((err as Error).message || "Unable to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const statusBadge = (s: string | undefined) => {
    switch (s) {
      case "approved":
        return (
          <span className="rounded-full bg-emerald-900/50 text-emerald-300 px-3 py-1 text-xs font-semibold uppercase">
            ✓ Approved
          </span>
        );
      case "rejected":
        return (
          <span className="rounded-full bg-red-900/50 text-red-300 px-3 py-1 text-xs font-semibold uppercase">
            ✗ Rejected
          </span>
        );
      case "pending":
        return (
          <span className="rounded-full bg-amber-900/50 text-amber-300 px-3 py-1 text-xs font-semibold uppercase">
            ⏳ Pending Review
          </span>
        );
      default:
        return (
          <span className="rounded-full bg-slate-800 text-slate-400 px-3 py-1 text-xs font-semibold uppercase">
            No Profile
          </span>
        );
    }
  };

  if (loading || (!user && !error)) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <p className="text-sm text-slate-400">Loading…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />
      <div className="mx-auto max-w-2xl px-4 py-10 space-y-8">
        {/* Header */}
        <header className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Driver Profile Setup</h1>
          <p className="text-sm text-slate-400">
            Enter your vehicle details and submit for admin review. You will be able to accept ride
            requests once your application is approved.
          </p>
        </header>

        {/* Verification status banner */}
        {!dataLoading && verification && (
          <div
            className={`rounded-xl border px-4 py-3 text-sm space-y-1 ${
              verification.status === "approved"
                ? "border-emerald-700 bg-emerald-950/30"
                : verification.status === "rejected"
                  ? "border-red-700 bg-red-950/30"
                  : "border-amber-700/50 bg-amber-950/20"
            }`}
          >
            <div className="flex items-center gap-2">
              {statusBadge(verification.status)}
            </div>
            <p className="text-slate-300 mt-1">{verification.message}</p>
            {verification.rejection_reason && (
              <p className="text-red-300 text-xs mt-1">
                Reason: {verification.rejection_reason}
              </p>
            )}
          </div>
        )}

        {/* Success / error feedback */}
        {message && (
          <div className="rounded-md bg-emerald-900/30 border border-emerald-700 px-3 py-2 text-xs text-emerald-200">
            {message}
          </div>
        )}
        {error && (
          <div
            className="rounded-md bg-red-900/30 border border-red-700 px-3 py-2 text-xs text-red-200"
            role="alert"
          >
            {error}
          </div>
        )}

        {/* Vehicle form */}
        <form onSubmit={handleSubmit} className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 space-y-5">
          <h2 className="text-sm font-semibold text-slate-200">Vehicle Information</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {(
              [
                { name: "vehicle_make", label: "Make", placeholder: "Toyota" },
                { name: "vehicle_model", label: "Model", placeholder: "Sienna" },
                { name: "vehicle_year", label: "Year", placeholder: "2020", type: "number" },
                { name: "vehicle_color", label: "Color", placeholder: "Silver" },
                { name: "license_plate", label: "License Plate", placeholder: "ABC-1234" },
              ] as { name: keyof VehicleForm; label: string; placeholder: string; type?: string }[]
            ).map(({ name, label, placeholder, type }) => (
              <div key={name} className="space-y-1">
                <label htmlFor={name} className="block text-xs font-medium text-slate-400">
                  {label}
                </label>
                <input
                  id={name}
                  name={name}
                  type={type ?? "text"}
                  value={form[name]}
                  onChange={handleChange}
                  placeholder={placeholder}
                  className="block w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            ))}

            <div className="space-y-1">
              <label htmlFor="vehicle_capacity" className="block text-xs font-medium text-slate-400">
                Passenger Capacity
              </label>
              <select
                id="vehicle_capacity"
                name="vehicle_capacity"
                value={form.vehicle_capacity}
                onChange={handleChange}
                className="block w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                  <option key={n} value={n}>
                    {n} passenger{n !== 1 ? "s" : ""}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Current stats (readonly) */}
          {profile && (
            <div className="rounded-md border border-slate-800 bg-slate-950/40 px-4 py-3 text-xs text-slate-400 space-y-1">
              <p>
                <span className="text-slate-300 font-medium">Total rides:</span> {profile.total_rides}
              </p>
              <p>
                <span className="text-slate-300 font-medium">Average rating:</span>{" "}
                {profile.average_rating > 0 ? `${profile.average_rating.toFixed(1)} / 5` : "No ratings yet"}
              </p>
            </div>
          )}

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-6 py-2 text-sm transition-colors"
            >
              {saving ? "Saving…" : profile ? "Update Profile" : "Submit Application"}
            </button>
          </div>
        </form>

        {/* Verification steps guide */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 space-y-3">
          <h2 className="text-sm font-semibold text-slate-200">Verification Process</h2>
          <ol className="list-decimal list-inside space-y-2 text-xs text-slate-400">
            <li>
              <span className="text-slate-300">Submit your vehicle details</span> using the form
              above.
            </li>
            <li>
              <span className="text-slate-300">Background check</span> — your diocesan coordinator
              or admin will initiate this step.
            </li>
            <li>
              <span className="text-slate-300">Safe Environment Training</span> — upload proof of
              completion to your coordinator.
            </li>
            <li>
              <span className="text-slate-300">Admin approval</span> — once verified, you will
              receive a notification and your status will show &ldquo;Approved.&rdquo;
            </li>
          </ol>
        </div>
      </div>
    </main>
  );
}
