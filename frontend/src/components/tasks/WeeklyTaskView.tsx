import { useMemo } from 'react';
import type { Task } from '../../types';

interface WeeklyTaskViewProps {
  tasks: Task[];
  onTaskClick: (taskId: string) => void;
  currentDate: Date;
}

const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 border-yellow-300';
    case 'in_progress':
      return 'bg-blue-100 border-blue-300';
    case 'completed':
      return 'bg-green-100 border-green-300';
    case 'verified':
      return 'bg-purple-100 border-purple-300';
    case 'on_hold':
      return 'bg-orange-100 border-orange-300';
    default:
      return 'bg-gray-100 border-gray-300';
  }
};

const getStatusTextColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'text-yellow-800';
    case 'in_progress':
      return 'text-blue-800';
    case 'completed':
      return 'text-green-800';
    case 'verified':
      return 'text-purple-800';
    case 'on_hold':
      return 'text-orange-800';
    default:
      return 'text-gray-800';
  }
};

const getDayOfWeek = (date: Date) => {
  const day = date.getDay();
  return day === 0 ? 6 : day - 1; // Convert Sunday (0) to 6, Monday (1) to 0, etc.
};

export function WeeklyTaskView({ tasks, onTaskClick, currentDate }: WeeklyTaskViewProps) {
  const weekStart = useMemo(() => {
    const date = new Date(currentDate);
    const dayOfWeek = getDayOfWeek(date);
    date.setDate(date.getDate() - dayOfWeek);
    date.setHours(0, 0, 0, 0);
    return date;
  }, [currentDate]);

  const weekTasks = useMemo(() => {
    const days: (Task | null)[][] = [[], [], [], [], [], [], []];
    
    tasks.forEach((task) => {
      if (task.due_date) {
        const dueDate = new Date(task.due_date);
        const dayOfWeek = getDayOfWeek(dueDate);
        
        // Check if task is in current week
        const taskWeekStart = new Date(dueDate);
        taskWeekStart.setDate(taskWeekStart.getDate() - dayOfWeek);
        taskWeekStart.setHours(0, 0, 0, 0);
        
        if (taskWeekStart.getTime() === weekStart.getTime()) {
          days[dayOfWeek].push(task);
        }
      }
    });
    
    return days;
  }, [tasks, weekStart]);

  const weekDays = useMemo(() => {
    return daysOfWeek.map((day, index) => {
      const date = new Date(weekStart);
      date.setDate(date.getDate() + index);
      return {
        name: day,
        date: date.getDate(),
        isToday: new Date().toDateString() === date.toDateString(),
      };
    });
  }, [weekStart]);

  const weekRange = useMemo(() => {
    const end = new Date(weekStart);
    end.setDate(end.getDate() + 6);
    const startStr = weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const endStr = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return `${startStr} - ${endStr}`;
  }, [weekStart]);

  const weekTaskCount = useMemo(() => {
    return tasks.filter(t => {
      if (!t.due_date) return false;
      const due = new Date(t.due_date);
      const day = getDayOfWeek(due);
      const start = new Date(due);
      start.setDate(start.getDate() - day);
      start.setHours(0, 0, 0, 0);
      return start.getTime() === weekStart.getTime();
    }).length;
  }, [tasks, weekStart]);

  return (
    <div className="space-y-4">
      {/* Week Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Week of {weekRange}
        </h3>
        <div className="text-sm text-gray-500">
          {weekTaskCount} tasks
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-2">
        {weekDays.map((day, index) => (
          <div key={day.name} className="text-center">
            <div className={`text-sm font-medium mb-2 ${day.isToday ? 'text-blue-600' : 'text-gray-600'}`}>
              {day.name}
            </div>
            <div className={`text-sm font-bold mb-2 ${day.isToday ? 'text-blue-600' : 'text-gray-900'}`}>
              {day.date}
            </div>
          </div>
        ))}
      </div>

      {/* Task Cards */}
      <div className="grid grid-cols-7 gap-2">
        {weekTasks.map((dayTasks, dayIndex) => (
          <div key={dayIndex} className="min-h-[120px] bg-gray-50 rounded-lg p-2 space-y-2">
            {dayTasks.length === 0 ? (
              <div className="text-center text-gray-400 text-xs py-4">
                No tasks
              </div>
            ) : (
              dayTasks.map((task) => task && (
                <button
                  key={task.id}
                  onClick={() => onTaskClick(task.id)}
                  className={`w-full text-left p-2 rounded-md border text-sm hover:shadow-md transition-shadow ${getStatusColor(task.status)}`}
                >
                  <div className="font-medium truncate">{task.title}</div>
                  <div className={`text-xs mt-1 capitalize ${getStatusTextColor(task.status)}`}>
                    {task.status.replace('_', ' ')}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {task.priority}
                  </div>
                </button>
              ))
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default WeeklyTaskView;
