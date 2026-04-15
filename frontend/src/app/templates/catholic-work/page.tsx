import Link from "next/link";
import { catholicWorkSource } from "@/lib/nonprofitSiteSources";

export default function CatholicWorkTemplatePage() {
  return (
    <main className="min-h-screen bg-white text-navy">
      <section className="bg-navy px-4 py-16 text-white">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-bold uppercase tracking-[0.25em] text-gold">
            {catholicWorkSource.heroLabel}
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
                  <a
                    key={cta.label}
                    href={cta.href}
                    target={cta.href.startsWith("http") ? "_blank" : undefined}
                    rel={cta.href.startsWith("http") ? "noopener noreferrer" : undefined}
                    className="inline-flex items-center justify-center border-2 border-gold bg-gold px-5 py-3 text-sm font-bold uppercase tracking-wide text-navy transition-colors hover:bg-gold-600 hover:border-gold-600"
                  >
                    {cta.label}
                  </a>
                ))}
              </div>
            </div>

            <aside className="border border-white/20 bg-white/10 p-6 backdrop-blur-sm">
              <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">
                Who Catholic.Work serves
              </p>
              <ul className="mt-4 space-y-4 text-sm leading-6 text-white/85">
                {catholicWorkSource.audience.map((item) => (
                  <li key={item} className="border-l-2 border-gold/60 pl-4">
                    {item}
                  </li>
                ))}
              </ul>
            </aside>
          </div>
        </div>
      </section>

      <section className="px-4 py-14">
        <div className="mx-auto grid max-w-6xl gap-12 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
              About the apostolate
            </p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
              A clearer path for discipleship in a digital age
            </h2>
            <p className="mt-5 text-base leading-7 text-slate-700">
              {catholicWorkSource.summary}
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              {catholicWorkSource.values.map((value) => (
                <div key={value.title} className="border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-bold uppercase tracking-[0.18em] text-marian">
                    {value.title}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-slate-700">{value.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="border-2 border-navy bg-white p-6">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">
              Why this page exists
            </p>
            <div className="mt-5 space-y-4 text-sm leading-7 text-slate-700">
              <p>
                This version turns the existing template into a concrete landing page for
                Catholic.Work, using the ministry language already reflected in the site&apos;s
                mission and about messaging.
              </p>
              <p>
                The structure is intentionally simple: explain the mission, show who it serves,
                present the core work, introduce the founder, and give visitors a direct next step.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-slate-50 px-4 py-14">
        <div className="mx-auto max-w-6xl">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">Core work</p>
          <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
            Four ways Catholic.Work builds up the Church
          </h2>
          <div className="mt-8 grid gap-6 lg:grid-cols-2">
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

      <section className="px-4 py-14">
        <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
              Leadership
            </p>
            <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
              Founded by a ministry leader working at the intersection of faith and technology
            </h2>
            <div className="mt-6 border-l-8 border-gold bg-gold-50 p-6">
              <p className="text-sm font-bold uppercase tracking-[0.18em] text-navy">
                {catholicWorkSource.founder.name}
              </p>
              <p className="mt-2 text-lg font-semibold text-navy">
                {catholicWorkSource.founder.role}
              </p>
              <p className="mt-4 text-sm leading-7 text-slate-700">
                {catholicWorkSource.founder.bio}
              </p>
              <a
                href={catholicWorkSource.founder.profileHref}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-5 inline-flex items-center justify-center bg-navy px-4 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-slate-800"
              >
                View LinkedIn Profile
              </a>
            </div>
          </div>

          <aside className="border-2 border-navy bg-navy p-6 text-white">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-gold">Explore</p>
            <ul className="mt-5 space-y-3 text-sm leading-6 text-white/85">
              {catholicWorkSource.featuredLinks.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-white underline decoration-gold underline-offset-4 hover:text-gold"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/templates"
                className="inline-flex items-center justify-center border border-white/40 px-4 py-3 text-sm font-bold uppercase tracking-wide text-white transition-colors hover:bg-white hover:text-navy"
              >
                Back to sources
              </Link>
              <a
                href="https://catholic.work"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center bg-gold px-4 py-3 text-sm font-bold uppercase tracking-wide text-navy transition-colors hover:bg-gold-600"
              >
                Open live site
              </a>
            </div>
          </aside>
        </div>
      </section>

      <section className="bg-slate-50 px-4 py-14">
        <div className="mx-auto max-w-6xl border-2 border-navy bg-white p-8">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-marian">
            Next step
          </p>
          <h2 className="mt-3 text-3xl font-black tracking-tight text-navy">
            Invite visitors to walk the Emmaus road with you
          </h2>
          <p className="mt-4 max-w-3xl text-base leading-7 text-slate-700">
            Catholic.Work&apos;s message is strongest when the next action is simple: learn more,
            connect with the founder, or visit the live apostolate site. This page keeps those
            actions visible without losing the spiritual and pastoral focus of the mission.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            {catholicWorkSource.callsToAction.map((cta) => (
              <a
                key={cta.label}
                href={cta.href}
                target={cta.href.startsWith("http") ? "_blank" : undefined}
                rel={cta.href.startsWith("http") ? "noopener noreferrer" : undefined}
                className="inline-flex items-center justify-center border-2 border-navy px-5 py-3 text-sm font-bold uppercase tracking-wide text-navy transition-colors hover:bg-navy hover:text-white"
              >
                {cta.label}
              </a>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
