import { httpClient } from './http-client';
import { Todo, TodoFilter, Status, Priority } from '@/types';

const API_URL = '/api/backend';

// Backend types
interface BackendTask {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: Priority;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

// Mapper functions
const mapBackendToTodo = (task: BackendTask): Todo => ({
  id: task.id.toString(),
  title: task.title,
  description: task.description || '',
  priority: task.priority,
  status: task.completed ? Status.COMPLETED : Status.TODO,
  dueDate: task.due_date ? new Date(task.due_date) : null,
  createdAt: new Date(task.created_at),
  subtasks: [], // Default
  tags: [], // Default
});

export const todoApi = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  getAll: async (_filter?: TodoFilter, _search?: string) => {
    // Backend doesn't support filter/search params in the generic getAll yet.
    const tasks = await httpClient.get<BackendTask[]>(`${API_URL}/tasks`);
    return tasks.map(mapBackendToTodo);
  },

  create: async (todo: Partial<Todo>) => {
    const payload = {
      title: todo.title,
      description: todo.description,
      priority: todo.priority || Priority.MEDIUM,
      due_date: todo.dueDate ? todo.dueDate.toISOString() : null,
    };
    const task = await httpClient.post<BackendTask>(`${API_URL}/tasks`, payload);
    return mapBackendToTodo(task);
  },

  update: async (id: string, todo: Partial<Todo>) => {
    let resultTask: BackendTask | null = null;

    if (todo.status !== undefined) {
      resultTask = await httpClient.patch<BackendTask>(`${API_URL}/tasks/${id}`, {
        completed: todo.status === Status.COMPLETED
      });
    }

    if (todo.title !== undefined || todo.description !== undefined || todo.priority !== undefined || todo.dueDate !== undefined) {
       const detailsPayload: Record<string, string | Priority | null | undefined> = {};
       if (todo.title !== undefined) detailsPayload.title = todo.title;
       if (todo.description !== undefined) detailsPayload.description = todo.description;
       if (todo.priority !== undefined) detailsPayload.priority = todo.priority;
       if (todo.dueDate !== undefined) detailsPayload.due_date = todo.dueDate ? todo.dueDate.toISOString() : null;

       resultTask = await httpClient.put<BackendTask>(`${API_URL}/tasks/${id}`, detailsPayload);
    }

    if (!resultTask) {
        throw new Error("No update performed");
    }

    return mapBackendToTodo(resultTask);
  },

  delete: (id: string) => 
    httpClient.delete(`${API_URL}/tasks/${id}`),

  toggleStatus: async (id: string, currentStatus: Status) => {
    const newCompleted = currentStatus !== Status.COMPLETED;
    const task = await httpClient.patch<BackendTask>(`${API_URL}/tasks/${id}`, { completed: newCompleted });
    return mapBackendToTodo(task);
  },
  
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  addSubtask: (_todoId: string, _title: string) => {
    console.warn("Subtasks not supported by backend");
    return Promise.resolve(); 
  }
};