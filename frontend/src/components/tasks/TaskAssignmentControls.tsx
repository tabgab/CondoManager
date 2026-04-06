import { useState } from 'react';
import type { User } from '../../types';

interface TaskAssignmentControlsProps {
  employees: User[];
  currentAssigneeId: string | null;
  onAssign?: (employeeId: string) => void;
  onUnassign?: () => void;
  isAssigning?: boolean;
}

export function TaskAssignmentControls({
  employees,
  currentAssigneeId,
  onAssign,
  onUnassign,
  isAssigning = false,
}: TaskAssignmentControlsProps) {
  const [selectedEmployee, setSelectedEmployee] = useState<string>('');

  const currentAssignee = employees.find(e => e.id === currentAssigneeId);

  const handleAssign = () => {
    if (selectedEmployee && onAssign && selectedEmployee !== currentAssigneeId) {
      onAssign(selectedEmployee);
    }
  };

  const isAssignDisabled = !selectedEmployee || 
    selectedEmployee === currentAssigneeId || 
    isAssigning;

  return (
    <div className="space-y-3">
      {/* Current Assignment */}
      <div className="text-sm">
        {currentAssignee ? (
          <div className="flex items-center justify-between bg-blue-50 px-3 py-2 rounded-md">
            <div>
              <span className="text-gray-500">Currently assigned to: </span>
              <span className="font-medium text-gray-900">
                {currentAssignee.first_name} {currentAssignee.last_name}
              </span>
              <span className="text-gray-400 text-xs ml-2">({currentAssignee.email})</span>
            </div>
            {onUnassign && (
              <button
                onClick={onUnassign}
                disabled={isAssigning}
                className="text-red-600 hover:text-red-800 text-xs font-medium disabled:opacity-50"
              >
                Unassign
              </button>
            )}
          </div>
        ) : (
          <div className="bg-yellow-50 px-3 py-2 rounded-md text-yellow-800 text-sm">
            Not assigned to any employee
          </div>
        )}
      </div>

      {/* Assignment Controls */}
      <div className="flex items-center gap-3">
        <label htmlFor="employee-select" className="sr-only">Assign to</label>
        <select
          id="employee-select"
          value={selectedEmployee}
          onChange={(e) => setSelectedEmployee(e.target.value)}
          disabled={isAssigning}
          className="flex-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md disabled:opacity-50"
        >
          <option value="">Select an employee...</option>
          {employees.map((employee) => (
            <option 
              key={employee.id} 
              value={employee.id}
              disabled={employee.id === currentAssigneeId}
            >
              {employee.first_name} {employee.last_name} ({employee.email})
              {employee.id === currentAssigneeId ? ' - Currently Assigned' : ''}
            </option>
          ))}
        </select>
        <button
          onClick={handleAssign}
          disabled={isAssignDisabled}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAssigning ? 'Assigning...' : 'Assign'}
        </button>
      </div>
    </div>
  );
}

export default TaskAssignmentControls;
