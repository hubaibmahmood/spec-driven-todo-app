"use client";
import { Menu, CheckSquare } from "lucide-react";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-8">
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} className="lg:hidden text-slate-500 hover:text-slate-700">
          <Menu className="w-6 h-6" />
        </button>

        <div className="flex items-center gap-2 text-indigo-600 font-bold text-xl">
          <CheckSquare className="w-8 h-8" />
          <span>Momentum</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Future: User menu, notifications, etc. */}
      </div>
    </header>
  );
}
