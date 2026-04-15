import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section - Flat, bold, high contrast */}
      <header className="safe-top bg-marian px-4 pt-14 pb-12 text-center">
        <div className="mx-auto max-w-lg">
          {/* Eucharist icon - matches favicon */}
          <div className="mx-auto mb-5 h-16 w-16 overflow-hidden rounded-full border-2 border-navy bg-navy">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" className="h-full w-full">
              {/* Dark navy square background */}
              <rect width="100" height="100" fill="#0A1628"/>
              {/* Dark navy circle - scaled to 95% of square */}
              <circle cx="50" cy="50" r="47.5" fill="#1A2434"/>
              {/* Golden icon group - scaled to fill ~85% of square */}
              <g transform="translate(50, 50) scale(0.85)" fill="#FBBF24">
                {/* Chalice cup/bowl */}
                <path d="M-20,-5 Q-20,8 0,12 Q20,8 20,-5 L20,-8 L-20,-8 Z"/>
                {/* Stem */}
                <path d="M-5,12 L-5,20 Q-8,22 -8,25 Q-8,28 -5,28 L5,28 Q8,28 8,25 Q8,22 5,20 L5,12 Z"/>
                {/* Base */}
                <path d="M-15,28 L-15,32 Q-15,35 0,35 Q15,35 15,32 L15,28 Q5,30 0,30 Q-5,30 -15,28 Z"/>
                {/* Host (Eucharist) */}
                <circle cx="0" cy="-18" r="12"/>
                {/* Sunburst rays */}
                <g stroke="#FBBF24" strokeWidth="1.5" strokeLinecap="round">
                  <line x1="0" y1="-34" x2="0" y2="-42"/>
                  <line x1="8" y1="-32" x2="12" y2="-40"/>
                  <line x1="14" y1="-26" x2="22" y2="-32"/>
                  <line x1="16" y1="-18" x2="26" y2="-18"/>
                  <line x1="14" y1="-10" x2="22" y2="-4"/>
                  <line x1="-8" y1="-32" x2="-12" y2="-40"/>
                  <line x1="-14" y1="-26" x2="-22" y2="-32"/>
                  <line x1="-16" y1="-18" x2="-26" y2="-18"/>
                  <line x1="-14" y1="-10" x2="-22" y2="-4"/>
                </g>
              </g>
              {/* Cross on cup - dark navy, centered on chalice bowl */}
              <g transform="translate(50, 50) scale(0.85)" fill="#1A2434">
                <rect x="-2" y="-4" width="4" height="12"/>
                <rect x="-6" y="0" width="12" height="4"/>
              </g>
            </svg>
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white sm:text-5xl">
            Catholic Ride Share
          </h1>
          <p className="mt-4 text-lg font-medium text-white/90">
            Get to Mass. Help others get there too.
          </p>
        </div>
      </header>

      {/* Main CTA Buttons - Flat, bold, no shadows */}
      <main className="px-4 py-8">
        <div className="mx-auto max-w-sm space-y-4">
          <Link
            href="/login"
            className="flex w-full items-center justify-center gap-3 rounded-none bg-gold px-6 py-5 text-xl font-bold text-navy uppercase tracking-wide transition-colors hover:bg-gold-600 active:bg-gold-600"
          >
            Sign In
          </Link>
          
          <Link
            href="/register"
            className="flex w-full items-center justify-center gap-3 rounded-none border-4 border-navy bg-white px-6 py-5 text-xl font-bold text-navy uppercase tracking-wide transition-colors hover:bg-navy hover:text-white active:bg-navy active:text-white"
          >
            Create Account
          </Link>
        </div>

        <div className="mx-auto mt-8 max-w-sm border-2 border-dashed border-marian bg-marian-50 p-5">
          <p className="text-sm font-bold uppercase tracking-wide text-navy">
            Need a nonprofit website template?
          </p>
          <p className="mt-2 text-sm text-slate-700">
            Preview the finished Catholic.Work promotional webpage built from the provided source
            material.
          </p>
          <Link
            href="/templates"
            className="mt-4 inline-flex items-center justify-center bg-navy px-4 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-slate-800"
          >
            Browse Templates
          </Link>
        </div>

        {/* Feature Cards - Flat with colored left borders */}
        <div className="mx-auto mt-12 max-w-lg space-y-0">
          <div className="border-l-8 border-marian bg-slate-100 p-6">
            <h3 className="text-xl font-bold text-navy uppercase tracking-wide">Request a Ride</h3>
            <p className="mt-2 text-base text-slate-700">
              Need a ride to Mass, Confession, or a parish event? Volunteer drivers are ready to help.
            </p>
          </div>

          <div className="border-l-8 border-gold bg-slate-50 p-6">
            <h3 className="text-xl font-bold text-navy uppercase tracking-wide">Offer Your Time</h3>
            <p className="mt-2 text-base text-slate-700">
              Drive fellow parishioners to the sacraments. Set your availability and serve.
            </p>
          </div>

          <div className="border-l-8 border-marian bg-slate-100 p-6">
            <h3 className="text-xl font-bold text-navy uppercase tracking-wide">Safe &amp; Trusted</h3>
            <p className="mt-2 text-base text-slate-700">
              Verified community members. Your privacy is protected.
            </p>
          </div>
        </div>
      </main>

      {/* Footer - Flat */}
      <footer className="safe-bottom bg-navy px-4 py-6 text-center">
        <p className="text-base font-medium italic text-white/90">
          &ldquo;I am among you as one who serves.&rdquo; – Lk 22:27
        </p>
        <p className="mt-4 text-sm text-white/90">
          © {new Date().getFullYear()}{" "}
          <a
            href="https://catholic.work"
            target="_blank"
            rel="noopener noreferrer"
            className="no-underline hover:text-white transition-colors"
          >
            Catholic.Work
          </a>
        </p>
      </footer>
    </div>
  );
}
