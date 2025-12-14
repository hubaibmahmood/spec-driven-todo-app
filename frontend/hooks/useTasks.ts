import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Todo, Status, Priority } from "@/types";
import { todoApi } from "@/lib/api-v2";
import { ApiRedirectError } from "@/lib/http-client";

export interface UseTasksReturn {
  todos: Todo[];
  isLoading: boolean;
  handleToggleStatus: (id: string) => Promise<void>;
  handleDelete: (id: string) => Promise<void>;
  handleSaveTodo: (taskData: Partial<Todo>, editingTodo?: Todo | null) => Promise<void>;
  handleEdit: (todo: Todo, onOpenModal: () => void, setEditingTodo: (todo: Todo | null) => void) => void;
  handleAddSubtask: (todoId: string, title: string) => void;
  refreshTodos: () => Promise<void>;
}

export function useTasks(): UseTasksReturn {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Fetch todos
  const loadTodos = useCallback(async () => {
    try {
      const data = await todoApi.getAll();
      setTodos(data);
    } catch (err) {
      console.error("Failed to load todos", err);
      if (err instanceof ApiRedirectError) {
        router.push(err.redirectUrl);
      }
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  // Toggle task status (complete/incomplete)
  const handleToggleStatus = useCallback(async (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const newStatus = todo.status === Status.COMPLETED ? Status.TODO : Status.COMPLETED;

    // Optimistic update
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
  }, [todos]);

  // Delete task
  const handleDelete = useCallback(async (id: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    const previousTodos = [...todos];

    // Optimistic update
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await todoApi.delete(id);
    } catch (error) {
      console.error("Failed to delete task", error);
      // Revert on error
      setTodos(previousTodos);
    }
  }, [todos]);

  // Save task (create or update)
  const handleSaveTodo = useCallback(async (taskData: Partial<Todo>, editingTodo?: Todo | null) => {
    try {
      if (editingTodo) {
        // Update existing task
        // Optimistic update
        setTodos(prev => prev.map(t =>
          t.id === editingTodo.id ? { ...t, ...taskData } as Todo : t
        ));

        // Call API
        const updated = await todoApi.update(editingTodo.id, taskData);
        setTodos(prev => prev.map(t => t.id === editingTodo.id ? updated : t));
      } else {
        // Create new task - Optimistic Update
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
          throw apiError;
        }
      }
    } catch (err) {
      console.error("Failed to save todo", err);
      alert("Failed to save task.");
    }
  }, []);

  // Edit task (opens modal)
  const handleEdit = useCallback((
    todo: Todo,
    onOpenModal: () => void,
    setEditingTodo: (todo: Todo | null) => void
  ) => {
    setEditingTodo(todo);
    onOpenModal();
  }, []);

  // Add subtask (not implemented in backend yet)
  const handleAddSubtask = useCallback((todoId: string, title: string) => {
    // Not implemented in backend yet
    console.log("Add subtask not implemented", todoId, title);
  }, []);

  // Manual refresh
  const refreshTodos = useCallback(async () => {
    setIsLoading(true);
    await loadTodos();
  }, [loadTodos]);

  return {
    todos,
    isLoading,
    handleToggleStatus,
    handleDelete,
    handleSaveTodo,
    handleEdit,
    handleAddSubtask,
    refreshTodos,
  };
}
