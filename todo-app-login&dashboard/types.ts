export enum Priority {
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High',
  URGENT = 'Urgent'
}

export enum Status {
  TODO = 'Todo',
  IN_PROGRESS = 'In Progress',
  COMPLETED = 'Completed'
}

export interface SubTask {
  id: string;
  title: string;
  completed: boolean;
}

export interface Todo {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  status: Status;
  dueDate: Date | null;
  createdAt: Date;
  subtasks: SubTask[];
  tags: string[];
}

export interface TodoStats {
  total: number;
  completed: number;
  pending: number;
  highPriority: number;
}

export type TodoFilter = 'All' | 'Active' | 'Completed';