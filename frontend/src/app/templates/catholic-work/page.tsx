import Link from "next/link";
import { catholicWorkSource } from "@/lib/nonprofitSiteSources";

export default function CatholicWorkTemplatePage() {
  return (
    <main className="min-h-screen bg-white text-navy">
      <section className="bg-navy px-4 py-16 text-white">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-bold uppercase tracking-[0.25em] text-gold">
            Static website template
          </p>
          <div className="mt-6 grid gap-10 lg:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.8fr)]">
            <div>
              <h1 className="text-4xl font-black tracking-tight sm:text-6xl">
                {catholicWorkSource.name}
              </h1>
              <p className="mt-5 max-w-3xl text-lg text-white/85 sm:text-xl">
                {catholicWorkSource.tagline}
              </p>
              <p className="mt-6 max-w-3xl text-base leading-7 text-white/75">
                {catholicWorkSource.mission}
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                {catholicWorkSource.callsToAction.map((cta) => (
                  <Link
                    key={cta.label}
                    href={cta.href}
                    className="inline-flex items-center justify-center border-2 border-gold bg-gold px-5 py-3 text-sm font-bold uppercase tracking-wide text-navy transition-colors hover:bg-gold-600 hover:border-gold-600"
                  >
                    {cta.label}
                  </Link>
                ))}
              </div>
            </div>

            <aside className="border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">
                Best use
              </p>
              <p className="mt-4 text-base leading-7 text-white/85">
                Use this page as a launch-ready template for a nonprofit landing page that
                introduces the mission, explains the ministry, and gives visitors simple next
                steps to engage.
              </p>
            </aside>
          </div>
        </div>
      </section>

      <section className="px-4 py-14">
        <div className="mx-auto grid max-w-6xl gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
              Mission
            </p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
              Faith, justice, and belonging in one clear story
            </h2>
            <p className="mt-5 text-base leading-7 text-slate-700">
              {catholicWorkSource.summary}
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {catholicWorkSource.audience.map((item) => (
              <div key={item} className="border-l-8 border-marian bg-slate-100 p-5">
                <p className="text-sm font-bold uppercase tracking-wide text-navy">Audience</p>
                <p className="mt-3 text-sm leading-6 text-slate-700">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-slate-50 px-4 py-14">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
            Core sections
          </p>
          <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
            Structure your page around the nonprofit&apos;s key work
          </h2>
          <div className="mt-8 grid gap-6 lg:grid-cols-3">
            {catholicWorkSource.pillars.map((pillar, index) => (
              <article key={pillar.title} className="border-2 border-navy bg-white p-6">
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">
                  0{index + 1}
                </p>
                <h3 className="mt-3 text-xl font-black text-navy">{pillar.title}</h3>
                <p className="mt-4 text-sm leading-6 text-slate-700">{pillar.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="get-involved" className="px-4 py-14">
        <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
              Get involved
            </p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
              Give visitors an immediate next step
            </h2>
            <div className="mt-6 space-y-4">
              <div className="border-l-8 border-gold bg-gold-50 p-5">
                <h3 className="text-lg font-bold text-navy">Join the community</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  Invite supporters to subscribe, attend an event, or connect with a local
                  chapter or partner group.
                </p>
              </div>
              <div className="border-l-8 border-marian bg-slate-100 p-5">
                <h3 className="text-lg font-bold text-navy">Support the mission</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  Provide a simple donation, sponsorship, or volunteer pathway with concise
                  reasons to act now.
                </p>
              </div>
              <div className="border-l-8 border-gold bg-gold-50 p-5">
                <h3 className="text-lg font-bold text-navy">Explore resources</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  Link visitors to featured programs, directories, articles, or educational
                  materials that deepen engagement.
                </p>
              </div>
            </div>
          </div>

          <aside className="border-2 border-navy bg-navy p-6 text-white">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">
              Template notes
            </p>
            <ul className="mt-5 space-y-4 text-sm leading-6 text-white/85">
              <li>Replace placeholder links with approved donation, signup, and contact URLs.</li>
              <li>Swap the overview copy for finalized language from your communications team.</li>
              <li>Add testimonials, impact numbers, or partner logos when those assets are ready.</li>
            </ul>
            <Link
              href="/templates"
              className="mt-8 inline-flex items-center justify-center border border-white/40 px-4 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-white hover:text-navy"
            >
              Back to sources
            </Link>
          </aside>
        </div>
      </section>
    </main>
  );
}
