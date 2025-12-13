"use client";

import { useMemo, Suspense } from "react";
import Link from "next/link";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { TaskList } from "@/components/dashboard/TaskList";
import { EmptyPreviewState } from "@/components/dashboard/EmptyStates";
import { Priority, Status } from "@/types";
import { useSession } from "@/lib/auth-client";
import { useTasks } from "@/hooks/useTasks";

function DashboardContent() {
  const { data: session } = useSession();

  // Use the tasks hook for all CRUD operations
  const {
    todos,
    isLoading,
    handleToggleStatus,
    handleDelete,
    handleAddSubtask,
  } = useTasks();

  // Calculate stats
  const stats = useMemo(() => {
    return {
      total: todos.length,
      completed: todos.filter(t => t.status === Status.COMPLETED).length,
      pending: todos.filter(t => t.status !== Status.COMPLETED).length,
      highPriority: todos.filter(t =>
        (t.priority === Priority.HIGH || t.priority === Priority.URGENT) &&
        t.status !== Status.COMPLETED
      ).length
    };
  }, [todos]);

  // Preview logic: Show today's tasks + overdue (max 8)
  const previewTodos = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Filter: overdue OR due today, incomplete only
    const relevantTasks = todos.filter(todo => {
      if (todo.status === Status.COMPLETED) return false;
      if (!todo.dueDate) return false;
      const dueDate = new Date(todo.dueDate);
      return dueDate < tomorrow; // Overdue or due today
    });

    // Sort: overdue first, then high priority, then by due date
    return relevantTasks
      .sort((a, b) => {
        const aDate = new Date(a.dueDate!);
        const bDate = new Date(b.dueDate!);

        // Overdue first
        const aOverdue = aDate < today;
        const bOverdue = bDate < today;
        if (aOverdue && !bOverdue) return -1;
        if (!aOverdue && bOverdue) return 1;

        // Then by priority (HIGH/URGENT first)
        const aPriority = a.priority === Priority.HIGH || a.priority === Priority.URGENT ? 1 : 0;
        const bPriority = b.priority === Priority.HIGH || b.priority === Priority.URGENT ? 1 : 0;
        if (aPriority > bPriority) return -1;
        if (aPriority < bPriority) return 1;

        // Then by due date
        return aDate.getTime() - bDate.getTime();
      })
      .slice(0, 8); // Show max 8 tasks
  }, [todos]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading tasks...</div>;
  }

  return (
    <>
      {/* Welcome Section */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">
          Good Morning, {session?.user?.name || 'User'}!
        </h1>
        <p className="text-slate-500">Here&apos;s what&apos;s on your plate for today.</p>
      </div>

      {/* Stats */}
      <DashboardStats stats={stats} />

      {/* Today's Focus Section */}
      <section className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-slate-900">Today&apos;s Focus</h2>
          <Link
            href="/dashboard/tasks"
            className="text-indigo-600 hover:text-indigo-700 text-sm font-medium transition-colors"
          >
            View All Tasks →
          </Link>
        </div>

        {previewTodos.length > 0 ? (
          <TaskList
            todos={previewTodos}
            onToggleStatus={handleToggleStatus}
            onDelete={handleDelete}
            onEdit={() => {}} // No edit from dashboard preview
            onAddSubtask={handleAddSubtask}
            previewMode={true}
          />
        ) : (
          <EmptyPreviewState taskCount={todos.length} />
        )}
      </section>
    </>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div>Loading dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}