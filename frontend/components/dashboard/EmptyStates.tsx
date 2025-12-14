"use client";

import Link from "next/link";
import { CheckCircle, Plus, Filter } from "lucide-react";

// Dashboard preview empty state (all caught up!)
export function EmptyPreviewState({ taskCount = 0 }: { taskCount?: number }) {
  return (
    <div className="text-center py-16 bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
        <CheckCircle className="w-8 h-8 text-indigo-600" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-1">All caught up!</h3>
      <p className="text-slate-600 mb-4">
        {taskCount > 0
          ? `You have ${taskCount} task${taskCount === 1 ? '' : 's'}, but none are due today or overdue.`
          : "You don't have any tasks yet."
        }
      </p>
      <Link
        href="/dashboard/tasks"
        className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
      >
        {taskCount > 0 ? 'View All Tasks' : 'Create Your First Task'}
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </Link>
    </div>
  );
}

// Tasks page empty state (no tasks at all)
export function EmptyTasksState({ onCreateTask }: { onCreateTask: () => void }) {
  return (
    <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4">
        <Plus className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-medium text-slate-900 mb-1">No tasks yet</h3>
      <p className="text-slate-500 max-w-sm mx-auto mb-6">
        Get started by creating your first task. Stay organized and boost your productivity!
      </p>
      <button
        onClick={onCreateTask}
        className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg shadow-sm transition-all font-medium"
      >
        <Plus className="w-5 h-5" />
        Create Your First Task
      </button>
    </div>
  );
}

// No results state (filters applied but no matches)
export function NoResultsState({ onClearFilters }: { onClearFilters: () => void }) {
  return (
    <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4">
        <Filter className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-medium text-slate-900 mb-1">No tasks match your filters</h3>
      <p className="text-slate-500 max-w-sm mx-auto mb-6">
        Try adjusting your search or filter criteria to find what you're looking for.
      </p>
      <button
        onClick={onClearFilters}
        className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
      >
        Clear Filters
      </button>
    </div>
  );
}
