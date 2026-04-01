"use client";

import Link from "next/link";
import { FormEvent, useState, useEffect } from "react";
import { registerUser, getDioceses, getParishes, Diocese, Parish } from "@/lib/api";

export default function RegisterPage() {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    phone: "",
    parish_id: "" as number | string,
  });
  const [dioceses, setDioceses] = useState<Diocese[]>([]);
  const [parishes, setParishes] = useState<Parish[]>([]);
  const [selectedDioceseId, setSelectedDioceseId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (field: keyof typeof form, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  useEffect(() => {
    getDioceses().then(setDioceses).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedDioceseId) {
      getParishes(Number(selectedDioceseId)).then(setParishes).catch(console.error);
    } else {
      setParishes([]);
    }
  }, [selectedDioceseId]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      await registerUser({
        email: form.email,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone || undefined,
        role: "rider",
        parish_id: Number(form.parish_id) || undefined,
      });
      setSuccess(
        "Account created. Please check your email for a verification code before signing in."
      );
    } catch (err) {
      setError((err as Error).message || "Unable to create account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-white">
      {/* Header bar */}
      <header className="bg-marian px-4 py-4">
        <Link href="/" className="text-lg font-bold text-white uppercase tracking-wide">
          ← Back
        </Link>
      </header>

      <div className="flex-1 px-4 py-8">
        <div className="mx-auto w-full max-w-lg">
          <h1 className="text-3xl font-black text-navy uppercase tracking-wide">
            Create Account
          </h1>
          <p className="mt-2 text-base text-slate-600">
            Join as a rider. Driver features unlock after verification.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div className="border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}
            {success && (
              <div className="border-l-4 border-green-600 bg-green-50 px-4 py-3 text-sm text-green-800">
                {success}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="first_name"
                  className="block text-sm font-bold text-navy uppercase tracking-wide"
                >
                  First Name
                </label>
                <input
                  id="first_name"
                  required
                  value={form.first_name}
                  onChange={(e) => handleChange("first_name", e.target.value)}
                  className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian"
                />
              </div>
              <div>
                <label
                  htmlFor="last_name"
                  className="block text-sm font-bold text-navy uppercase tracking-wide"
                >
                  Last Name
                </label>
                <input
                  id="last_name"
                  required
                  value={form.last_name}
                  onChange={(e) => handleChange("last_name", e.target.value)}
                  className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-bold text-navy uppercase tracking-wide"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={form.email}
                onChange={(e) => handleChange("email", e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian"
              />
            </div>

            <div>
              <label
                htmlFor="phone"
                className="block text-sm font-bold text-navy uppercase tracking-wide"
              >
                Phone <span className="font-normal normal-case">(optional)</span>
              </label>
              <input
                id="phone"
                type="tel"
                value={form.phone}
                onChange={(e) => handleChange("phone", e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-navy uppercase tracking-wide">
                Diocese
              </label>
              <select
                required
                value={selectedDioceseId}
                onChange={(e) => setSelectedDioceseId(e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy focus:outline-none focus:border-marian"
              >
                <option value="">Select your diocese</option>
                {dioceses.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.state})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-bold text-navy uppercase tracking-wide">
                Parish
              </label>
              <select
                required
                disabled={!selectedDioceseId}
                value={form.parish_id}
                onChange={(e) => handleChange("parish_id", Number(e.target.value))}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy focus:outline-none focus:border-marian disabled:bg-slate-100 disabled:text-slate-500"
              >
                <option value="">Select your parish</option>
                {parishes.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} {p.city ? `- ${p.city}` : ""}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-bold text-navy uppercase tracking-wide"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => handleChange("password", e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-none bg-gold px-6 py-4 text-lg font-bold text-navy uppercase tracking-wide transition-colors hover:bg-gold-600 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Creating..." : "Create Account"}
            </button>
          </form>

          <p className="mt-6 text-sm text-slate-600">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-marian hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}


