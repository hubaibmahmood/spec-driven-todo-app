"use client";

import { TodoFilter } from "@/types";
import { Search } from "lucide-react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

export function FilterBar() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();

  const filter = (searchParams.get('filter') as TodoFilter) || 'All';
  const search = searchParams.get('search') || '';

  const handleFilterChange = (term: TodoFilter) => {
    const params = new URLSearchParams(searchParams);
    if (term === 'All') {
        params.delete('filter');
    } else {
        params.set('filter', term);
    }
    replace(`${pathname}?${params.toString()}`);
  };

  const handleSearchChange = (term: string) => {
    const params = new URLSearchParams(searchParams);
    if (term) {
      params.set('search', term);
    } else {
      params.delete('search');
    }
    replace(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex gap-2 p-1 bg-slate-100 rounded-lg w-full sm:w-auto">
        {(['All', 'Active', 'Completed'] as TodoFilter[]).map((f) => (
          <button
            key={f}
            onClick={() => handleFilterChange(f)}
            className={`flex-1 sm:flex-none px-4 py-1.5 text-sm font-medium rounded-md transition-all ${filter === f ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="relative w-full sm:w-64">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input 
          type="text" 
          placeholder="Search tasks..." 
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
        />
      </div>
    </div>
  );
}
