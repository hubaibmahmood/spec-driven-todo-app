"use client";

import { useState, Suspense } from "react";
import { Plus } from "lucide-react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useTasks } from "@/hooks/useTasks";
import { TaskList } from "@/components/dashboard/TaskList";
import { FilterBar } from "@/components/dashboard/FilterBar";
import { AddTodoModal } from "@/components/todo/AddTodoModal";
import { Pagination } from "@/components/dashboard/Pagination";
import { EmptyTasksState, NoResultsState } from "@/components/dashboard/EmptyStates";
import { Priority, Todo, TodoFilter } from "@/types";

const ITEMS_PER_PAGE = 20;

function TasksContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  // Read filter params from URL
  const filter = (searchParams.get('filter') as TodoFilter) || 'All';
  const search = searchParams.get('search') || '';
  const priority = searchParams.get('priority') as Priority | null;
  const currentPage = Number(searchParams.get('page')) || 1;

  // Map URL filter to completed boolean for backend
  const completedParam =
    filter === 'Completed' ? true :
    filter === 'Active' ? false :
    undefined;

  // Fetch with server-side filtering
  const {
    todos: paginatedTodos,
    total,
    totalPages,
    isLoading,
    handleToggleStatus,
    handleDelete,
    handleSaveTodo,
    handleEdit,
    handleAddSubtask,
  } = useTasks({
    search: search || undefined,
    priority: priority || undefined,
    completed: completedParam,
    page: currentPage,
    limit: ITEMS_PER_PAGE,
  });

  const hasActiveFilters = filter !== 'All' || search !== '' || priority !== null;

  // Handle modal open for new task
  const handleOpenModal = () => {
    setEditingTodo(null);
    setIsModalOpen(true);
  };

  // Handle edit (wrapper for handleEdit from hook)
  const onEdit = (todo: Todo) => {
    handleEdit(todo, () => setIsModalOpen(true), setEditingTodo);
  };

  // Handle save (wrapper for handleSaveTodo from hook)
  const onSaveTodo = async (taskData: Partial<Todo>) => {
    await handleSaveTodo(taskData, editingTodo);
    setIsModalOpen(false);
    setEditingTodo(null);
  };

  // Clear filters
  const handleClearFilters = () => {
    router.push(pathname);
  };

  // Loading state
  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading tasks...</div>;
  }

  // Empty state - no tasks and no active filters
  if (paginatedTodos.length === 0 && !hasActiveFilters) {
    return (
      <>
        <EmptyTasksState onCreateTask={handleOpenModal} />
        <AddTodoModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={onSaveTodo}
          initialData={editingTodo}
        />
      </>
    );
  }

  // No results state - filters applied but no matches
  if (paginatedTodos.length === 0 && hasActiveFilters) {
    return (
      <>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">All Tasks</h1>
            <p className="text-slate-500">Manage and organize your tasks</p>
          </div>
          <button
            onClick={handleOpenModal}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg shadow-sm transition-all"
          >
            <Plus className="w-5 h-5" />
            <span>New Task</span>
          </button>
        </div>

        <FilterBar />

        <NoResultsState onClearFilters={handleClearFilters} />

        <AddTodoModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={onSaveTodo}
          initialData={editingTodo}
        />
      </>
    );
  }

  // Main render with tasks
  return (
    <>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">All Tasks</h1>
          <p className="text-slate-500">
            {total} {total === 1 ? 'task' : 'tasks'}
            {hasActiveFilters && ' matching your filters'}
          </p>
        </div>
        <button
          onClick={handleOpenModal}
          className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg shadow-sm transition-all"
        >
          <Plus className="w-5 h-5" />
          <span>New Task</span>
        </button>
      </div>

      {/* Filters & Search */}
      <FilterBar />

      {/* Task List */}
      <TaskList
        todos={paginatedTodos}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
        onEdit={onEdit}
        onAddSubtask={handleAddSubtask}
      />

      {/* Pagination */}
      <Pagination currentPage={currentPage} totalPages={totalPages} />

      {/* Modal */}
      <AddTodoModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={onSaveTodo}
        initialData={editingTodo}
      />
    </>
  );
}

export default function TasksPage() {
  return (
    <Suspense fallback={<div>Loading tasks...</div>}>
      <TasksContent />
    </Suspense>
  );
}
