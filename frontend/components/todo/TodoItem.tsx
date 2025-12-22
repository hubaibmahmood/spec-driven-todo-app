"use client";

import React, { useState } from 'react';
import { Todo, Priority, Status } from '@/types';
import {
  CheckCircle2,
  Circle,
  MoreVertical,
  Trash2,
  Edit3,
  Calendar
} from 'lucide-react';
import { getUserTimezone } from '@/lib/utils/timezone';

interface TodoItemProps {
  todo: Todo;
  onToggleStatus: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: Todo) => void;
  onAddSubtask: (todoId: string, title: string) => void;
}

export function TodoItem({ todo, onToggleStatus, onDelete, onEdit }: TodoItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const priorityColor = {
    [Priority.LOW]: 'bg-slate-100 text-slate-600',
    [Priority.MEDIUM]: 'bg-blue-50 text-blue-600',
    [Priority.HIGH]: 'bg-orange-50 text-orange-600',
    [Priority.URGENT]: 'bg-red-50 text-red-600',
  };

  // Format due date with time if it has a time component (not midnight UTC)
  const formatDueDate = (date: Date | null): string => {
    if (!date) return '';

    const dateObj = new Date(date);
    const timezone = getUserTimezone();

    // Check if the date has a meaningful time component (not midnight UTC)
    const hasTime = dateObj.getUTCHours() !== 0 || dateObj.getUTCMinutes() !== 0;

    if (hasTime) {
      // Show date and time
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        timeZone: timezone,
        hour12: true
      }).format(dateObj);
    } else {
      // Show only date
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        timeZone: timezone
      }).format(dateObj);
    }
  };



  return (
    <div className={`bg-white rounded-xl border transition-all duration-200 ${todo.status === Status.COMPLETED ? 'border-slate-100 opacity-60' : 'border-slate-200 shadow-sm hover:shadow-md'}`}>
      <div className="p-4">
        <div className="flex items-start gap-4">
          <button 
            onClick={() => onToggleStatus(todo.id)}
            className={`mt-1 flex-shrink-0 transition-colors ${todo.status === Status.COMPLETED ? 'text-green-500' : 'text-slate-300 hover:text-indigo-500'}`}
          >
            {todo.status === Status.COMPLETED ? <CheckCircle2 className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
          </button>

          <div className="flex-1 min-w-0" onClick={() => setIsExpanded(!isExpanded)}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className={`font-semibold text-lg text-slate-900 ${todo.status === Status.COMPLETED ? 'line-through text-slate-500' : ''}`}>
                  {todo.title}
                </h3>
                <p className="text-slate-500 text-sm mt-1 line-clamp-2">{todo.description}</p>
              </div>
              
              <div className="relative ml-2">
                <button 
                  onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu); }}
                  className="p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-100"
                >
                  <MoreVertical className="w-5 h-5" />
                </button>
                
                {showMenu && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={(e) => {e.stopPropagation(); setShowMenu(false);}} />
                    <div className="absolute right-0 top-8 w-32 bg-white border border-slate-200 rounded-lg shadow-lg z-20 py-1">
                      <button 
                        onClick={(e) => { e.stopPropagation(); setShowMenu(false); onEdit(todo); }}
                        className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                      >
                        <Edit3 className="w-4 h-4" /> Edit
                      </button>
                      <button 
                        onClick={(e) => { e.stopPropagation(); setShowMenu(false); onDelete(todo.id); }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                      >
                        <Trash2 className="w-4 h-4" /> Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 mt-3">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColor[todo.priority]}`}>
                {todo.priority}
              </span>

              {todo.dueDate && (
                <span className="flex items-center gap-1 text-xs text-slate-500 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-100">
                  <Calendar className="w-3 h-3" />
                  {formatDueDate(todo.dueDate)}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Subtasks Section */}
        {todo.subtasks.length > 0 && (
          <div className={`mt-4 pl-10 space-y-2 border-t border-slate-50 pt-3 transition-all ${isExpanded ? 'block' : 'hidden'}`}>
             <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Subtasks</p>
             {todo.subtasks.map(sub => (
               <div key={sub.id} className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full border flex items-center justify-center ${sub.completed ? 'bg-indigo-500 border-indigo-500' : 'border-slate-300'}`}>
                    {sub.completed && <CheckCircle2 className="w-3 h-3 text-white" />}
                  </div>
                  <span className={`text-sm ${sub.completed ? 'text-slate-400 line-through' : 'text-slate-600'}`}>{sub.title}</span>
               </div>
             ))}
          </div>
        )}
      </div>
    </div>
  );
}
