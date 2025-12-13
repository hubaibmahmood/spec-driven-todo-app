"use client";

import { useState, useMemo, Suspense } from "react";
import { Plus } from "lucide-react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useTasks } from "@/hooks/useTasks";
import { TaskList } from "@/components/dashboard/TaskList";
import { FilterBar } from "@/components/dashboard/FilterBar";
import { AddTodoModal } from "@/components/todo/AddTodoModal";
import { Pagination } from "@/components/dashboard/Pagination";
import { EmptyTasksState, NoResultsState } from "@/components/dashboard/EmptyStates";
import { Todo, TodoFilter, Status } from "@/types";

const ITEMS_PER_PAGE = 20;

function TasksContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  // Get tasks data from hook
  const {
    todos,
    isLoading,
    handleToggleStatus,
    handleDelete,
    handleSaveTodo,
    handleEdit,
    handleAddSubtask,
  } = useTasks();

  // Get URL params
  const filter = (searchParams.get('filter') as TodoFilter) || 'All';
  const search = searchParams.get('search') || '';
  const currentPage = Number(searchParams.get('page')) || 1;

  // Filter todos based on search and filter params
  const filteredTodos = useMemo(() => {
    return todos.filter(todo => {
      const matchesSearch = todo.title.toLowerCase().includes(search.toLowerCase()) ||
                          todo.tags.some(tag => tag.toLowerCase().includes(search.toLowerCase()));

      const matchesFilter =
        filter === 'All' ? true :
        filter === 'Completed' ? todo.status === Status.COMPLETED :
        todo.status !== Status.COMPLETED;

      return matchesSearch && matchesFilter;
    });
  }, [todos, filter, search]);

  // Calculate pagination
  const totalPages = Math.ceil(filteredTodos.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedTodos = filteredTodos.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Check if current page is out of bounds (can happen after filtering)
  if (currentPage > totalPages && totalPages > 0) {
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', '1');
    router.push(`${pathname}?${params.toString()}`);
  }

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

  // Empty state - no tasks at all
  if (todos.length === 0) {
    return <EmptyTasksState onCreateTask={handleOpenModal} />;
  }

  // No results state - filters applied but no matches
  const hasActiveFilters = filter !== 'All' || search !== '';
  if (filteredTodos.length === 0 && hasActiveFilters) {
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
            {filteredTodos.length} {filteredTodos.length === 1 ? 'task' : 'tasks'}
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
