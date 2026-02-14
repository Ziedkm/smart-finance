import { FlagIcon, PlusIcon } from '@heroicons/react/24/outline';

interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string;
  category: string;
  progress: number;
  status: 'on-track' | 'at-risk' | 'completed';
}

export function Goals() {
  const goals: Goal[] = [
    {
      id: '1',
      name: 'Emergency Fund',
      target_amount: 10000,
      current_amount: 6500,
      deadline: '2026-12-31',
      category: 'Savings',
      progress: 65,
      status: 'on-track',
    },
    {
      id: '2',
      name: 'Vacation to Paris',
      target_amount: 5000,
      current_amount: 3200,
      deadline: '2026-08-01',
      category: 'Travel',
      progress: 64,
      status: 'on-track',
    },
    {
      id: '3',
      name: 'New Laptop',
      target_amount: 3000,
      current_amount: 800,
      deadline: '2026-05-01',
      category: 'Technology',
      progress: 27,
      status: 'at-risk',
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'on-track':
        return 'bg-green-100 text-green-800';
      case 'at-risk':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Financial Goals</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track and achieve your savings and investment goals
          </p>
        </div>
        <button className="btn-primary flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          New Goal
        </button>
      </div>

      {/* Goals grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {goals.map((goal) => (
          <div key={goal.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="p-2 rounded-lg bg-primary-100">
                  <FlagIcon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {goal.name}
                  </h3>
                  <p className="text-sm text-gray-500">{goal.category}</p>
                </div>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(
                  goal.status
                )}`}
              >
                {goal.status.replace('-', ' ')}
              </span>
            </div>

            <div className="space-y-4">
              {/* Progress */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Progress</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {goal.progress}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      goal.status === 'at-risk' ? 'bg-yellow-500' : 'bg-primary-600'
                    }`}
                    style={{ width: `${goal.progress}%` }}
                  />
                </div>
              </div>

              {/* Amount */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500">Current</p>
                  <p className="text-lg font-bold text-gray-900">
                    {goal.current_amount.toFixed(0)} TND
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Target</p>
                  <p className="text-lg font-bold text-gray-900">
                    {goal.target_amount.toFixed(0)} TND
                  </p>
                </div>
              </div>

              {/* Deadline */}
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Deadline</span>
                  <span className="font-medium text-gray-900">
                    {new Date(goal.deadline).toLocaleDateString('en-GB')}
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {Math.ceil(
                    (new Date(goal.deadline).getTime() - Date.now()) /
                      (1000 * 60 * 60 * 24)
                  )}{' '}
                  days remaining
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
