import React, { useState, useMemo } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Layout from './components/Layout';
import Auth from './components/Auth';
import DashboardStats from './components/DashboardStats';
import TodoItem from './components/TodoItem';
import AddTodoModal from './components/AddTodoModal';
import { Todo, Priority, Status, TodoFilter, SubTask } from './types';
import { Plus, Search, Filter } from 'lucide-react';

// Initial Mock Data
const INITIAL_TODOS: Todo[] = [
  {
    id: '1',
    title: 'Review Project Requirements',
    description: 'Go through the latest PRD and update the technical specs document.',
    priority: Priority.HIGH,
    status: Status.TODO,
    dueDate: new Date(),
    createdAt: new Date(),
    subtasks: [],
    tags: ['work', 'planning']
  },
  {
    id: '2',
    title: 'Weekly Team Sync',
    description: 'Prepare slides for the engineering all-hands meeting.',
    priority: Priority.MEDIUM,
    status: Status.COMPLETED,
    dueDate: new Date(Date.now() - 86400000), // Yesterday
    createdAt: new Date(),
    subtasks: [],
    tags: ['meeting']
  }
];

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [todos, setTodos] = useState<Todo[]>(INITIAL_TODOS);
  const [filter, setFilter] = useState<TodoFilter>('All');
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

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

  // Handlers
  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = () => setIsAuthenticated(false);

  const handleAddTodo = (taskData: Partial<Todo>) => {
    if (editingTodo) {
      setTodos(prev => prev.map(t => t.id === editingTodo.id ? { ...t, ...taskData } as Todo : t));
    } else {
      const newTodo: Todo = {
        id: uuidv4(),
        title: taskData.title!,
        description: taskData.description || '',
        priority: taskData.priority || Priority.MEDIUM,
        status: Status.TODO,
        dueDate: taskData.dueDate || null,
        createdAt: new Date(),
        subtasks: [],
        tags: taskData.tags || []
      };
      setTodos(prev => [newTodo, ...prev]);
    }
    setEditingTodo(null);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      setTodos(prev => prev.filter(t => t.id !== id));
    }
  };

  const handleToggleStatus = (id: string) => {
    setTodos(prev => prev.map(t => {
      if (t.id === id) {
        return { ...t, status: t.status === Status.COMPLETED ? Status.TODO : Status.COMPLETED };
      }
      return t;
    }));
  };

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
    setIsModalOpen(true);
  };

  const handleAddSubtask = (todoId: string, title: string) => {
    setTodos(prev => prev.map(t => {
      if (t.id === todoId) {
        const newSub: SubTask = { id: uuidv4(), title, completed: false };
        return { ...t, subtasks: [...t.subtasks, newSub] };
      }
      return t;
    }));
  };

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <Layout onLogout={handleLogout}>
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Good Morning, User!</h1>
          <p className="text-slate-500">Here's what's on your plate for today.</p>
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
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex gap-2 p-1 bg-slate-100 rounded-lg w-full sm:w-auto">
          {(['All', 'Active', 'Completed'] as TodoFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`flex-1 sm:flex-none px-4 py-1.5 text-sm font-medium rounded-md transition-all ${filter === f ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search tasks..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
          />
        </div>
      </div>

      {/* Todo List */}
      <div className="space-y-4 pb-12">
        {filteredTodos.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-50 mb-4">
              <Filter className="w-8 h-8 text-slate-300" />
            </div>
            <h3 className="text-lg font-medium text-slate-900">No tasks found</h3>
            <p className="text-slate-500 max-w-sm mx-auto mt-1">Try adjusting your filters or create a new task to get started.</p>
          </div>
        ) : (
          filteredTodos.map(todo => (
            <TodoItem 
              key={todo.id} 
              todo={todo} 
              onToggleStatus={handleToggleStatus}
              onDelete={handleDelete}
              onEdit={handleEdit}
              onAddSubtask={handleAddSubtask}
            />
          ))
        )}
      </div>

      <AddTodoModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSave={handleAddTodo}
        initialData={editingTodo}
      />
    </Layout>
  );
};

export default App;