import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Requirement Compiler",
  description: "Transform natural language into application blueprints",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased min-h-screen flex flex-col relative`}>
        {/* Background glow effects */}
        <div className="absolute top-0 inset-x-0 h-64 bg-accent-blue/10 blur-[100px] pointer-events-none -z-10" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent-cyan/10 blur-[120px] pointer-events-none -z-10" />
        
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
