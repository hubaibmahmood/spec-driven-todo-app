"use client";

import React from 'react';
import { TodoStats } from '@/types';
import { PieChart, Pie, Cell } from 'recharts';
import { CheckSquare, Clock, AlertCircle } from 'lucide-react';

interface DashboardStatsProps {
  stats: TodoStats;
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const data = [
    { name: 'Completed', value: stats.completed },
    { name: 'Pending', value: stats.pending },
  ];

  const COLORS = ['#10b981', '#6366f1'];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Stat Card 1: Total */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Total Tasks</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-2">{stats.total}</h3>
        </div>
        <div className="mt-4 flex items-center text-sm text-slate-600">
          <span className="bg-slate-100 p-1.5 rounded-md mr-2">
            <CheckSquare className="w-4 h-4 text-slate-600" />
          </span>
          All tracked tasks
        </div>
      </div>

      {/* Stat Card 2: Completion Rate (Pie) */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
        <div className="flex flex-col justify-center h-full">
          <p className="text-sm font-medium text-slate-500">Progress</p>
          <h3 className="text-3xl font-bold text-slate-900 mt-2">
            {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}%
          </h3>
          <p className="text-xs text-slate-400 mt-1">Completion Rate</p>
        </div>
        <div className="h-24 w-24">
          <PieChart width={96} height={96}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={25}
              outerRadius={40}
              fill="#8884d8"
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </div>
      </div>

      {/* Stat Card 3: Pending High Priority */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">High Priority</p>
          <h3 className="text-3xl font-bold text-orange-600 mt-2">{stats.highPriority}</h3>
        </div>
        <div className="mt-4 flex items-center text-sm text-orange-700/80">
          <span className="bg-orange-50 p-1.5 rounded-md mr-2">
            <AlertCircle className="w-4 h-4 text-orange-600" />
          </span>
          Needs attention
        </div>
      </div>

      {/* Stat Card 4: Pending */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Pending</p>
          <h3 className="text-3xl font-bold text-indigo-600 mt-2">{stats.pending}</h3>
        </div>
        <div className="mt-4 flex items-center text-sm text-indigo-700/80">
          <span className="bg-indigo-50 p-1.5 rounded-md mr-2">
            <Clock className="w-4 h-4 text-indigo-600" />
          </span>
          Tasks remaining
        </div>
      </div>
    </div>
  );
}
