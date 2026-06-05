"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CodeBracketIcon, ChartBarIcon, BeakerIcon } from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth/AuthProvider";
import { useState, useRef, useEffect } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const navItems = [
    { name: "Compiler", href: "/", icon: CodeBracketIcon },
    { name: "Runs", href: "/runs", icon: ChartBarIcon },
    { name: "Evaluation", href: "/eval", icon: BeakerIcon },
  ];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200 glass-dark">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center text-white font-bold text-xl shadow-[0_0_15px_rgba(220,38,38,0.3)]">
            A
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-900 hidden sm:inline-block">
            AI Application Architect
          </span>
        </div>

        <div className="flex items-center gap-4">
          <nav className="flex items-center gap-1 sm:gap-2 mr-4">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-slate-200 text-slate-900 shadow-inner"
                      : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="hidden md:inline-block">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {user ? (
            <div className="relative" ref={dropdownRef}>
              <button 
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-3 hover:bg-slate-100 p-1.5 rounded-full transition-colors"
              >
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-bold text-slate-900 leading-none">{user.name || user.email}</div>
                  <div className="text-xs text-red-600 font-medium capitalize mt-1">{user.role}</div>
                </div>
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt="Avatar" className="w-9 h-9 rounded-full border border-slate-200 object-cover" />
                ) : (
                  <div className="w-9 h-9 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-600 font-bold">
                    {(user.name || user.email).charAt(0).toUpperCase()}
                  </div>
                )}
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-50">
                  <Link href="/profile" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors">Profile</Link>
                  <Link href="/settings" className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors">Settings</Link>
                  <div className="border-t border-slate-100 my-1"></div>
                  <button onClick={logout} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium">Logout</button>
                </div>
              )}
            </div>
          ) : (
            <Link href="/login" className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors shadow-sm">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
