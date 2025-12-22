"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, CheckSquare, X, LogOut } from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
  user?: {
    name: string;
    email: string;
    image?: string | null;
  } | null;
}

export function Sidebar({ isOpen, onClose, onLogout, user }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <>
      {/* Mobile Sidebar Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-30
        w-64 bg-white border-r border-slate-200 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-full flex flex-col">
          <div className="p-6 flex items-center justify-between border-b border-slate-100">
            <div className="flex items-center gap-2 text-indigo-600 font-bold text-xl">
              <CheckSquare className="w-8 h-8" />
              <span>Momentum</span>
            </div>
            <button onClick={onClose} className="lg:hidden text-slate-400 hover:text-slate-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            <Link
              href="/dashboard"
              onClick={onClose}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                isActive('/dashboard')
                  ? 'text-indigo-600 bg-indigo-50'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              Dashboard
            </Link>
            <Link
              href="/dashboard/tasks"
              onClick={onClose}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                isActive('/dashboard/tasks')
                  ? 'text-indigo-600 bg-indigo-50'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <CheckSquare className="w-5 h-5" />
              My Tasks
            </Link>
          </nav>

          <div className="p-4 border-t border-slate-100">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold overflow-hidden">
                {user?.image ? (
                   // eslint-disable-next-line @next/next/no-img-element
                   <img src={user.image} alt={user.name} className="w-full h-full object-cover" />
                ) : (
                   user?.name?.substring(0, 2).toUpperCase() || 'US'
                )}
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.name || 'User'}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email || 'user@example.com'}</p>
              </div>
              <button 
                onClick={onLogout}
                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
