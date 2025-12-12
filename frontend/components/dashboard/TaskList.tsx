"use client";

import { Todo } from "@/types";
import { TodoItem } from "../todo/TodoItem";
import { Filter } from "lucide-react";

interface TaskListProps {
  todos: Todo[];
  onToggleStatus: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: Todo) => void;
  onAddSubtask: (todoId: string, title: string) => void;
}

export function TaskList({ todos, onToggleStatus, onDelete, onEdit, onAddSubtask }: TaskListProps) {
  if (todos.length === 0) {
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

  return (
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
  );
}
