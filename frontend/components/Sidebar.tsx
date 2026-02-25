"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/upload", label: "Upload Dataset" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/model-results", label: "Model Results" },
  { href: "/explainability", label: "Explainability" },
  { href: "/chatbot", label: "Chatbot" },
  { href: "/download-report", label: "Download Report" }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="min-h-screen w-64 border-r border-slate-800 bg-slate-950 p-4">
      <h1 className="mb-6 text-xl font-bold text-cyan-400">AI Data Analyst</h1>
      <nav className="space-y-2">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`block rounded-md px-3 py-2 text-sm ${
                active ? "bg-cyan-500 text-slate-950" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
