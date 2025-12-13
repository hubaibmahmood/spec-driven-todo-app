"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { Plus } from "lucide-react";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { TaskList } from "@/components/dashboard/TaskList";
import { AddTodoModal } from "@/components/todo/AddTodoModal";
import { FilterBar } from "@/components/dashboard/FilterBar";
import { Todo, TodoFilter, Priority, Status } from "@/types";
import { todoApi } from "@/lib/api-v2";
import { ApiRedirectError } from "@/lib/http-client"; // Import the new error type
import { useSession } from "@/lib/auth-client";
import { useSearchParams, useRouter } from "next/navigation"; // Import useRouter

function DashboardContent() {
  const { data: session } = useSession();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  
  const searchParams = useSearchParams();
  const filter = (searchParams.get('filter') as TodoFilter) || 'All';
  const search = searchParams.get('search') || '';
  const router = useRouter(); // Initialize router

  // Fetch data
  useEffect(() => {
    async function loadTodos() {
        try {
            const data = await todoApi.getAll();
            setTodos(data);
        } catch (err) {
            console.error("Failed to load todos", err);
            if (err instanceof ApiRedirectError) {
                router.push(err.redirectUrl); // Redirect to the URL provided by the error (which is /login)
            }
        } finally {
            setIsLoading(false);
        }
    }
    loadTodos();
  }, [filter, search, router]); // Add router to dependencies

  // Derived State: Stats
  const stats = useMemo(() => {
    return {
      total: todos.length,
      completed: todos.filter(t => t.status === Status.COMPLETED).length,
      pending: todos.filter(t => t.status !== Status.COMPLETED).length,
      highPriority: todos.filter(t => t.priority === Priority.HIGH || t.priority === Priority.URGENT).filter(t => t.status !== Status.COMPLETED).length
    };
  }, [todos]);

  // Derived State: Filtered Todos
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

  const handleToggleStatus = async (id: string) => {
    // Optimistic update
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const newStatus = todo.status === Status.COMPLETED ? Status.TODO : Status.COMPLETED;
    
    setTodos(prev => prev.map(t => 
      t.id === id ? { ...t, status: newStatus } : t
    ));

    try {
      await todoApi.toggleStatus(id, todo.status);
    } catch (error) {
      // Revert on error
      console.error("Failed to toggle status", error);
      setTodos(prev => prev.map(t => 
        t.id === id ? { ...t, status: todo.status } : t
      ));
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    const previousTodos = [...todos];
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await todoApi.delete(id);
    } catch (error) {
      console.error("Failed to delete task", error);
      setTodos(previousTodos);
    }
  };

  const handleSaveTodo = async (taskData: Partial<Todo>) => {
    try {
        if (editingTodo) {
            // Update
            // Optimistic
            setTodos(prev => prev.map(t => t.id === editingTodo.id ? { ...t, ...taskData } as Todo : t));

            // Call API
            const updated = await todoApi.update(editingTodo.id, taskData);
            setTodos(prev => prev.map(t => t.id === editingTodo.id ? updated : t));
        } else {
            // Create - Optimistic Update
            const tempId = `temp-${Date.now()}`;
            const optimisticTodo: Todo = {
                id: tempId,
                title: taskData.title || '',
                description: taskData.description || '',
                status: Status.TODO,
                priority: taskData.priority || Priority.MEDIUM,
                dueDate: taskData.dueDate || null,
                tags: taskData.tags || [],
                subtasks: [],
                createdAt: new Date(),
            };

            // Add optimistic task immediately
            setTodos(prev => [optimisticTodo, ...prev]);

            try {
                // Call API
                const newTodo = await todoApi.create(taskData);

                // Replace optimistic task with real one from server
                setTodos(prev => prev.map(t => t.id === tempId ? newTodo : t));
            } catch (apiError) {
                // Remove optimistic task on error
                setTodos(prev => prev.filter(t => t.id !== tempId));
                throw apiError; // Re-throw to be caught by outer catch
            }
        }
    } catch (err) {
        console.error("Failed to save todo", err);
        alert("Failed to save task.");
    }

    setEditingTodo(null);
  };

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
    setIsModalOpen(true);
  };

  const handleAddSubtask = (todoId: string, title: string) => {
    // Not implemented in backend yet
  };

  if (isLoading) {
      return <div className="flex items-center justify-center h-full">Loading tasks...</div>;
  }

  return (
    <>
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Good Morning, {session?.user?.name || 'User'}!</h1>
          <p className="text-slate-500">Here&apos;s what&apos;s on your plate for today.</p>
        </div>
        <button 
          onClick={() => { setEditingTodo(null); setIsModalOpen(true); }}
          className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg shadow-sm transition-all"
        >
          <Plus className="w-5 h-5" />
          <span>New Task</span>
        </button>
      </div>

      {/* Stats */}
      <DashboardStats stats={stats} />

      {/* Filters & Search */}
      <FilterBar />

      {/* Todo List */}
      <TaskList 
        todos={filteredTodos}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
        onEdit={handleEdit}
        onAddSubtask={handleAddSubtask}
      />

      <AddTodoModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSave={handleSaveTodo}
        initialData={editingTodo}
      />
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