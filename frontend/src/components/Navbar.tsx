"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Consult", icon: "⚡" },
  { href: "/explore", label: "Explore", icon: "🔍" },
  { href: "/graph", label: "Graph", icon: "◉" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-white/70 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-linear-to-br from-accent to-purple-500 flex items-center justify-center shadow-sm">
            <span className="text-white text-sm font-bold">G</span>
          </div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-bold text-foreground text-[15px] tracking-tight">Graph-RAG</span>
            <span className="text-muted text-[11px] font-medium hidden sm:inline tracking-wide uppercase">
              Clinical AI
            </span>
          </div>
        </Link>
        <nav className="flex items-center gap-1 bg-card-hover/60 rounded-xl p-1 border border-border/50">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-4 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-200 ${
                pathname === link.href
                  ? "bg-white text-accent shadow-sm border border-border/60"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <span className="mr-1.5 text-xs">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
