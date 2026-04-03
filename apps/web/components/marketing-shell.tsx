import type { ReactNode } from "react";
import Link from "next/link";

type MarketingShellProps = {
  children: ReactNode;
  eyebrow?: string;
  title?: string;
  description?: string;
};

const links = [
  { href: "/", label: "Home" },
  { href: "/product", label: "Product" },
  { href: "/pricing", label: "Pricing" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" }
];

export function MarketingShell({ children, eyebrow, title, description }: MarketingShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh" />
      <div className="mx-auto max-w-[1500px] px-4 py-6 lg:px-6">
        <header className="glass sticky top-4 z-20 rounded-[30px] px-6 py-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-accent">AtlasBI</p>
              <Link href="/" className="mt-2 block font-display text-2xl text-white">
                Global AI Business Intelligence
              </Link>
            </div>
            <nav className="flex flex-wrap items-center gap-5 text-sm text-slate-300">
              {links.map((link) => (
                <Link key={link.href} href={link.href} className="transition hover:text-white">
                  {link.label}
                </Link>
              ))}
              <Link
                href="/login"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:border-accent/60 hover:bg-white/10"
              >
                Login
              </Link>
            </nav>
          </div>
        </header>

        {(eyebrow || title || description) ? (
          <section className="mt-6 glass rounded-[34px] p-8 lg:p-10">
            {eyebrow ? <p className="text-xs uppercase tracking-[0.35em] text-accent">{eyebrow}</p> : null}
            {title ? <h1 className="mt-4 max-w-4xl font-display text-5xl leading-tight text-white lg:text-6xl">{title}</h1> : null}
            {description ? <p className="mt-5 max-w-3xl text-base leading-7 text-slate-300">{description}</p> : null}
          </section>
        ) : null}

        <div className="mt-6">{children}</div>

        <footer className="mt-8 glass rounded-[30px] px-6 py-8">
          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-accent">AtlasBI</p>
              <h2 className="mt-3 font-display text-3xl text-white">A global intelligence platform for modern revenue teams.</h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400">
                Company discovery, enrichment, AI search, opportunities, exports, alerts, and governed enterprise operations in one platform.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-accent">Explore</p>
                <div className="mt-4 space-y-2 text-sm text-slate-300">
                  {links.map((link) => (
                    <div key={link.href}>
                      <Link href={link.href} className="transition hover:text-white">
                        {link.label}
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-accent">Platform</p>
                <div className="mt-4 space-y-2 text-sm text-slate-300">
                  <p>AI Search</p>
                  <p>Signals and Opportunities</p>
                  <p>Customer Workspaces</p>
                  <p>Superadmin Operations</p>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
