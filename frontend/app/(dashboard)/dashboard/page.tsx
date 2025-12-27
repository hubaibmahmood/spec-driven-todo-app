"use client";

import { useMemo, Suspense } from "react";
import Link from "next/link";
import { Priority, Status, Todo } from "@/types";
import { useSession } from "@/lib/auth-client";
import { useTasks } from "@/hooks/useTasks";
import {
  CheckCircle2,
  Clock,
  ListTodo,
  AlertTriangle,
  Edit2,
  Trash2,
  Calendar,
  MoreVertical,
} from "lucide-react";

// Types
interface Stats {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
}

// Utility Functions
function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatUpcomingDate(date: Date): string {
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const isToday = date.toDateString() === today.toDateString();
  const isTomorrow = date.toDateString() === tomorrow.toDateString();

  if (isToday) {
    return `Today • ${formatTime(date)}`;
  } else if (isTomorrow) {
    return `Tomorrow • ${formatTime(date)}`;
  } else {
    return (
      date.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
      " • " +
      formatTime(date)
    );
  }
}

// Stats Card Component
function StatsCard({
  icon: Icon,
  label,
  value,
  accentColor,
  bgColor,
}: {
  icon: any;
  label: string;
  value: number;
  accentColor: string;
  bgColor: string;
}) {
  return (
    <div className="group relative bg-white rounded-2xl p-6 shadow-sm border border-stone-100 hover:shadow-xl hover:scale-[1.02] transition-all duration-300">
      <div
        className={`absolute top-0 left-0 w-1 h-full ${accentColor} rounded-l-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
      />

      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-stone-500 mb-2">{label}</p>
          <p className="text-4xl font-bold text-stone-900 tracking-tight">
            {value}
          </p>
        </div>

        <div
          className={`p-3 rounded-xl ${bgColor} group-hover:scale-110 transition-transform duration-300`}
        >
          <Icon className={`w-6 h-6 ${accentColor.replace("bg-", "text-")}`} />
        </div>
      </div>
    </div>
  );
}

// Priority Badge Component
function PriorityBadge({ priority }: { priority: Priority }) {
  const styles = {
    [Priority.URGENT]: "bg-rose-50 text-rose-700 border-rose-200",
    [Priority.HIGH]: "bg-orange-50 text-orange-700 border-orange-200",
    [Priority.MEDIUM]: "bg-amber-50 text-amber-700 border-amber-200",
    [Priority.LOW]: "bg-emerald-50 text-emerald-700 border-emerald-200",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[priority]}`}
    >
      {priority}
    </span>
  );
}

// Task Item Component
function TaskItem({
  todo,
  onToggleStatus,
  onDelete,
  onEdit,
  showTime = false,
  showEdit = true,
}: {
  todo: Todo;
  onToggleStatus: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: Todo) => void;
  showTime?: boolean;
  showEdit?: boolean;
}) {
  const isCompleted = todo.status === Status.COMPLETED;

  return (
    <div className="group bg-white rounded-xl p-4 border border-stone-100 hover:border-indigo-200 hover:shadow-md transition-all duration-200">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <button
          onClick={() => onToggleStatus(todo.id)}
          className={`flex-shrink-0 w-5 h-5 rounded-full border-2 mt-0.5 transition-all duration-200 ${
            isCompleted
              ? "bg-emerald-500 border-emerald-500"
              : "border-stone-300 hover:border-indigo-400"
          }`}
        >
          {isCompleted && (
            <CheckCircle2 className="w-full h-full text-white p-0.5" />
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1 min-w-0">
              <h3
                className={`font-semibold text-stone-900 mb-1 ${isCompleted ? "line-through opacity-50" : ""}`}
              >
                {todo.title}
              </h3>
              {todo.description && (
                <p className={`text-sm text-stone-600 ${isCompleted ? "opacity-50" : ""}`}>
                  {todo.description}
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex-shrink-0">
              {showEdit && (
                <button
                  onClick={() => onEdit(todo)}
                  className="p-1.5 rounded-lg hover:bg-stone-100 transition-colors"
                >
                  <Edit2 className="w-4 h-4 text-stone-400" />
                </button>
              )}
              <button
                onClick={() => onDelete(todo.id)}
                className="p-1.5 rounded-lg hover:bg-rose-50 transition-colors"
              >
                <Trash2 className="w-4 h-4 text-rose-400" />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap mt-3">
            <PriorityBadge priority={todo.priority} />
            {showTime && todo.dueDate && (
              <div className="flex items-center gap-1.5 text-sm text-stone-500">
                <Clock className="w-3.5 h-3.5" />
                <span>{formatTime(todo.dueDate)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Progress Chart Component (Simple Donut Chart)
function TaskProgress({
  completed,
  pending,
}: {
  completed: number;
  pending: number;
}) {
  const total = completed + pending;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-sm">
      <h3 className="text-lg font-bold text-stone-900 mb-6">Task Progress</h3>

      <div className="flex items-center gap-6">
        {/* Donut Chart on Left */}
        <div className="relative w-32 h-32 flex-shrink-0">
          <svg className="w-full h-full -rotate-90">
            {/* Background circle */}
            <circle
              cx="64"
              cy="64"
              r="45"
              stroke="#f5f5f4"
              strokeWidth="12"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="64"
              cy="64"
              r="45"
              stroke="url(#progressGradient)"
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient
                id="progressGradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-3xl font-bold text-stone-900">{percentage}%</p>
            </div>
          </div>
        </div>

        {/* Legend on Right */}
        <div className="space-y-4 flex-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-indigo-500 to-indigo-500" />
              <span className="text-sm font-medium text-stone-600">
                Completed
              </span>
            </div>
            <span className="text-xl font-bold text-stone-900">{completed}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-stone-200" />
              <span className="text-sm font-medium text-stone-600">Pending</span>
            </div>
            <span className="text-xl font-bold text-stone-900">{pending}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Upcoming Task Item
function UpcomingTaskItem({ todo }: { todo: Todo }) {
  const priorityColors = {
    [Priority.URGENT]: "bg-rose-500",
    [Priority.HIGH]: "bg-orange-500",
    [Priority.MEDIUM]: "bg-amber-500",
    [Priority.LOW]: "bg-emerald-500",
  };

  return (
    <div className="group flex items-start gap-3 p-3 rounded-lg hover:bg-stone-50 transition-colors duration-200 cursor-pointer">
      <div
        className={`w-2 h-2 rounded-full mt-2 ${priorityColors[todo.priority]}`}
      />
      <div className="flex-1 min-w-0">
        <p className="font-medium text-stone-900 text-sm truncate mb-1">
          {todo.title}
        </p>
        <p className="text-xs text-stone-500">
          {todo.dueDate && formatUpcomingDate(todo.dueDate)}
        </p>
      </div>
    </div>
  );
}

// Main Dashboard Content
function DashboardContent() {
  const { data: session } = useSession();
  const {
    todos,
    isLoading,
    handleToggleStatus,
    handleDelete,
    handleAddSubtask,
  } = useTasks();

  // Calculate stats
  const stats = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    return {
      total: todos.length,
      completed: todos.filter((t) => t.status === Status.COMPLETED).length,
      pending: todos.filter((t) => t.status !== Status.COMPLETED).length,
      overdue: todos.filter((t) => {
        if (t.status === Status.COMPLETED || !t.dueDate) return false;
        return t.dueDate < today;
      }).length,
    };
  }, [todos]);

  // Today's tasks
  const todaysTasks = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    return todos
      .filter((todo) => {
        if (todo.status === Status.COMPLETED || !todo.dueDate) return false;
        return todo.dueDate >= today && todo.dueDate < tomorrow;
      })
      .sort((a, b) => a.dueDate!.getTime() - b.dueDate!.getTime());
  }, [todos]);

  // Upcoming tasks
  const upcomingTasks = useMemo(() => {
    const now = new Date();
    const tomorrow = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() + 1,
    );

    return todos
      .filter((todo) => {
        if (todo.status === Status.COMPLETED || !todo.dueDate) return false;
        return todo.dueDate >= tomorrow;
      })
      .sort((a, b) => a.dueDate!.getTime() - b.dueDate!.getTime())
      .slice(0, 5);
  }, [todos]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-stone-500">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-indigo-50/30 px-4 py-5">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="animate-fade-in">
          <h1 className="text-3xl font-bold text-stone-900 mb-1">
            Good morning, {session?.user?.name || "User"}! 👋
          </h1>
          <p className="text-md text-stone-500">
            You have {todaysTasks.length} task
            {todaysTasks.length !== 1 ? "s" : ""} pending today
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-slide-up">
          <StatsCard
            icon={ListTodo}
            label="Total Tasks"
            value={stats.total}
            accentColor="bg-indigo-500"
            bgColor="bg-indigo-300"
          />
          <StatsCard
            icon={CheckCircle2}
            label="Completed"
            value={stats.completed}
            accentColor="bg-emerald-800"
            bgColor="bg-emerald-300"
          />
          <StatsCard
            icon={Clock}
            label="Pending"
            value={stats.pending}
            accentColor="bg-amber-500"
            bgColor="bg-amber-300"
          />
          <StatsCard
            icon={AlertTriangle}
            label="Overdue"
            value={stats.overdue}
            accentColor="bg-rose-500"
            bgColor="bg-rose-300"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Today's Tasks */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-stone-900">
                  Today's Tasks
                </h2>
                <p className="text-sm text-stone-500 mt-1">
                  {todaysTasks.length} remaining
                </p>
              </div>
              <Link
                href="/dashboard/tasks"
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 hover:shadow-lg hover:scale-105 transition-all duration-200"
              >
                View All →
              </Link>
            </div>

            {todaysTasks.length > 0 ? (
              <div className="space-y-3">
                {todaysTasks.map((todo) => (
                  <TaskItem
                    key={todo.id}
                    todo={todo}
                    onToggleStatus={handleToggleStatus}
                    onDelete={handleDelete}
                    onEdit={() => {}}
                    showTime={true}
                    showEdit={false}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-stone-100 p-12 text-center">
                <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 className="w-8 h-8 text-indigo-600" />
                </div>
                <h3 className="text-lg font-semibold text-stone-900 mb-2">
                  All caught up!
                </h3>
                <p className="text-stone-500">No tasks due today. Great job!</p>
              </div>
            )}
          </div>

          {/* Right Column - Widgets */}
          <div className="space-y-6">
            {/* Progress Widget */}
            <TaskProgress completed={stats.completed} pending={stats.pending} />

            {/* Upcoming Tasks Widget */}
            <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-sm">
              <div className="flex items-center gap-2 mb-6">
                <Calendar className="w-5 h-5 text-indigo-600" />
                <h3 className="text-lg font-bold text-stone-900">
                  Upcoming Tasks
                </h3>
              </div>

              {upcomingTasks.length > 0 ? (
                <div className="space-y-1">
                  {upcomingTasks.map((todo) => (
                    <UpcomingTaskItem key={todo.id} todo={todo} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-sm text-stone-400">No upcoming tasks</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }

        .animate-slide-up {
          animation: slide-up 0.8s ease-out;
        }
      `}</style>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-screen">
          <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
