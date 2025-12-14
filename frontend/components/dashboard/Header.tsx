"use client";
import { Menu } from "lucide-react";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-8">
      <button onClick={onMenuClick} className="lg:hidden text-slate-500 hover:text-slate-700">
        <Menu className="w-6 h-6" />
      </button>
      
      <div className="flex items-center justify-end w-full gap-4">
      </div>
    </header>
  );
}
