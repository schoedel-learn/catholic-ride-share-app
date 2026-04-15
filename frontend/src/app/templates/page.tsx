import Link from "next/link";
import { nonprofitSiteSources } from "@/lib/nonprofitSiteSources";

export default function TemplateSelectionPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-12">
      <div className="mx-auto max-w-5xl">
        <div className="max-w-3xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
            Static Website Sources
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight text-navy sm:text-5xl">
            Select a nonprofit page source
          </h1>
          <p className="mt-4 text-lg text-slate-700">
            Choose a source below to preview a static promotional and informational page
            template.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {nonprofitSiteSources.map((source) => (
            <article key={source.slug} className="border-2 border-navy bg-white p-6">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
                Promotional + informational
              </p>
              <h2 className="mt-3 text-2xl font-black text-navy">{source.name}</h2>
              <p className="mt-3 text-base text-slate-700">{source.tagline}</p>
              <p className="mt-4 text-sm text-slate-600">{source.summary}</p>

              <ul className="mt-6 space-y-2 text-sm text-slate-700">
                {source.highlights.map((highlight) => (
                  <li key={highlight} className="flex gap-2">
                    <span className="font-bold text-gold">■</span>
                    <span>{highlight}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-6">
                <Link
                  href={`/templates/${source.slug}`}
                  className="inline-flex items-center justify-center bg-gold px-4 py-3 text-sm font-bold uppercase tracking-wide text-navy transition-colors hover:bg-gold-600"
                >
                  Open Template
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
