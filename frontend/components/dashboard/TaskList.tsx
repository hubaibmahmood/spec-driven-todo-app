"use client";

import { Todo } from "@/types";
import { TodoItem } from "../todo/TodoItem";
import { Filter } from "lucide-react";
import Link from "next/link";

interface TaskListProps {
  todos: Todo[];
  onToggleStatus: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: Todo) => void;
  onAddSubtask: (todoId: string, title: string) => void;
  previewMode?: boolean;      // When true: render without empty state wrapper
  showViewAll?: boolean;       // When true: show "View All Tasks →" link
}

export function TaskList({
  todos,
  onToggleStatus,
  onDelete,
  onEdit,
  onAddSubtask,
  previewMode = false,
  showViewAll = false
}: TaskListProps) {
  // In preview mode, don't show empty state
  if (todos.length === 0 && !previewMode) {
    return (
      <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4">
          <Filter className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="text-lg font-medium text-slate-900">No tasks found</h3>
        <p className="text-slate-500 max-w-sm mx-auto mt-1">Try adjusting your filters or create a new task to get started.</p>
      </div>
    );
  }

  // In preview mode with no tasks, return null (let parent handle empty state)
  if (todos.length === 0 && previewMode) {
    return null;
  }

  return (
    <>
      <div className="space-y-4 pb-12">
        {todos.map(todo => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggleStatus={onToggleStatus}
            onDelete={onDelete}
            onEdit={onEdit}
            onAddSubtask={onAddSubtask}
          />
        ))}
      </div>

      {showViewAll && (
        <div className="text-center mt-6">
          <Link
            href="/dashboard/tasks"
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            View All Tasks
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      )}
    </>
  );
}
