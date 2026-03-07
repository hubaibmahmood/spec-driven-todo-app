"use client";

import { Priority, TodoFilter } from "@/types";
import { Search } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

const PRIORITY_OPTIONS: { label: string; value: string }[] = [
  { label: "All Priorities", value: "" },
  { label: "Urgent", value: Priority.URGENT },
  { label: "High", value: Priority.HIGH },
  { label: "Medium", value: Priority.MEDIUM },
  { label: "Low", value: Priority.LOW },
];

export function FilterBar() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();

  const filter = (searchParams.get('filter') as TodoFilter) || 'All';
  const search = searchParams.get('search') || '';
  const priority = searchParams.get('priority') || '';

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete('page'); // Reset to page 1 on filter change
    replace(`${pathname}?${params.toString()}`);
  };

  const handleFilterChange = (term: TodoFilter) => {
    const params = new URLSearchParams(searchParams.toString());
    if (term === 'All') {
      params.delete('filter');
    } else {
      params.set('filter', term);
    }
    params.delete('page');
    replace(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      {/* Status tabs */}
      <Tabs
        value={filter}
        onValueChange={(value) => handleFilterChange(value as TodoFilter)}
        className="w-full sm:w-auto"
      >
        <TabsList>
          <TabsTrigger value="All">All</TabsTrigger>
          <TabsTrigger value="Active">Active</TabsTrigger>
          <TabsTrigger value="Completed">Completed</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto sm:ml-auto">
        {/* Priority dropdown */}
        <select
          value={priority}
          onChange={(e) => updateParam('priority', e.target.value)}
          className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
        >
          {PRIORITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Search input */}
        <div className="relative w-full sm:w-56">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => updateParam('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
          />
        </div>
      </div>
    </div>
  );
}
