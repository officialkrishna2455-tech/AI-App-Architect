"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CodeBracketIcon, ChartBarIcon, BeakerIcon } from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Compiler", href: "/", icon: CodeBracketIcon },
    { name: "Runs", href: "/runs", icon: ChartBarIcon },
    { name: "Evaluation", href: "/eval", icon: BeakerIcon },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 glass-dark">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-accent-cyan to-accent-blue flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            RC
          </div>
          <span className="text-xl font-bold tracking-tight text-white hidden sm:inline-block">
            Requirement Compiler
          </span>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-white/10 text-white shadow-inner"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                )}
              >
                <item.icon className="w-5 h-5" />
                <span className="hidden md:inline-block">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
