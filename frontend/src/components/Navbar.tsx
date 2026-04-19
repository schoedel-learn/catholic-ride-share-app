"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  if (!user) return null;

  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/donate", label: "Donate" },
    { href: "/profile", label: "Profile" },
  ];

  if (
    user.role === "driver" ||
    user.role === "both" ||
    user.role === "admin"
  ) {
    links.push({ href: "/driver-profile", label: "Driver Profile" });
  }

  if (user.role === "admin" || user.role === "coordinator") {
    links.push({ href: "/admin", label: "Admin" });
  }

  return (
    <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
      <div className="mx-auto max-w-6xl px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-1">
          <Link
            href="/dashboard"
            className="text-sm font-bold text-emerald-400 mr-4 tracking-tight"
          >
            CRS
          </Link>
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                pathname === link.href
                  ? "bg-slate-800 text-slate-100"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            {user.email}
          </span>
          <button
            type="button"
            onClick={() => {
              logout();
              window.location.href = "/login";
            }}
            className="text-xs rounded-md border border-slate-700 px-3 py-1.5 text-slate-300 hover:bg-slate-800 hover:text-slate-100 transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
