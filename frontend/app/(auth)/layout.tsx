"use client";

import { usePathname } from "next/navigation";
import { CheckSquare } from "lucide-react";
import { DotPattern } from "@/components/ui/dot-pattern";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  // Full-width pages that should not be wrapped in a card
  const fullWidthPages = ["/verify-email", "/email-verified"];
  const isFullWidth = fullWidthPages.includes(pathname);

  // For full-width pages, just render children without the card wrapper
  if (isFullWidth) {
    return <>{children}</>;
  }

  // For other auth pages (login, register), use the card layout
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 relative">
      <DotPattern opacity={0.15} />
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100 relative z-10">
        <div className="p-8 pb-0">
          <div className="flex justify-center mb-8">
            <div className="flex items-center gap-2 text-indigo-600 font-bold text-2xl">
              <CheckSquare className="w-8 h-8" />
              <span>Momentum</span>
            </div>
          </div>
        </div>
        {children}
        <div className="bg-slate-50 p-4 border-t border-slate-100 text-center text-xs text-slate-400">
          © 2026 Momentum. Secure & Encrypted.
        </div>
      </div>
    </div>
  );
}
