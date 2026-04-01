"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError((err as Error).message || "Unable to sign in");
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

      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <h1 className="text-3xl font-black text-navy uppercase tracking-wide">Sign In</h1>
          <p className="mt-2 text-base text-slate-600">
            Welcome back. Enter your credentials.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div className="border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}

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
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian focus:ring-0"
              />
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
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-2 block w-full rounded-none border-2 border-navy bg-white px-4 py-3 text-base text-navy placeholder-slate-400 focus:outline-none focus:border-marian focus:ring-0"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-none bg-gold px-6 py-4 text-lg font-bold text-navy uppercase tracking-wide transition-colors hover:bg-gold-600 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between text-sm">
            <Link href="/forgot-password" className="font-medium text-marian hover:underline">
              Forgot password?
            </Link>
            <Link href="/register" className="font-medium text-marian hover:underline">
              Create account
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}


