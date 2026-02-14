import { useState } from 'react';
import { PlusIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { getCategoryIcon } from '../utils/categories';

interface Budget {
  id: string;
  category: string;
  amount: number;
  spent: number;
  period: 'weekly' | 'monthly' | 'yearly';
  alert_threshold: number;
  variance: number;
}

export function Budgets() {
  const [budgets] = useState<Budget[]>([
    {
      id: '1',
      category: 'Groceries',
      amount: 800,
      spent: 850,
      period: 'monthly',
      alert_threshold: 80,
      variance: 50,
    },
    {
      id: '2',
      category: 'Transport',
      amount: 500,
      spent: 450,
      period: 'monthly',
      alert_threshold: 80,
      variance: -50,
    },
    {
      id: '3',
      category: 'Dining',
      amount: 400,
      spent: 380,
      period: 'monthly',
      alert_threshold: 80,
      variance: -20,
    },
    {
      id: '4',
      category: 'Bills & Utilities',
      amount: 600,
      spent: 620,
      period: 'monthly',
      alert_threshold: 90,
      variance: 20,
    },
    {
      id: '5',
      category: 'Entertainment',
      amount: 300,
      spent: 250,
      period: 'monthly',
      alert_threshold: 80,
      variance: -50,
    },
  ]);

  const totalBudget = budgets.reduce((sum, b) => sum + b.amount, 0);
  const totalSpent = budgets.reduce((sum, b) => sum + b.spent, 0);
  const totalVariance = totalSpent - totalBudget;
  const adherence = ((totalBudget - Math.abs(totalVariance)) / totalBudget) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budgets</h1>
          <p className="mt-1 text-sm text-gray-500">
            Set and track spending limits by category
          </p>
        </div>
        <button className="btn-primary flex items-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          Create Budget
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-primary-100">
              <ChartBarIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Budget</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalBudget.toFixed(0)} TND
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Spent</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalSpent.toFixed(0)} TND
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div
              className={`p-3 rounded-lg ${
                totalVariance > 0 ? 'bg-red-100' : 'bg-green-100'
              }`}
            >
              <ChartBarIcon
                className={`h-6 w-6 ${
                  totalVariance > 0 ? 'text-red-600' : 'text-green-600'
                }`}
              />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Adherence</p>
              <p
                className={`text-2xl font-bold ${
                  adherence >= 90
                    ? 'text-green-600'
                    : adherence >= 70
                    ? 'text-yellow-600'
                    : 'text-red-600'
                }`}
              >
                {adherence.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Budget list */}
      <div className="space-y-4">
        {budgets.map((budget) => {
          const percentage = (budget.spent / budget.amount) * 100;
          const isOver = percentage > 100;
          const isWarning = percentage >= budget.alert_threshold;

          return (
            <div
              key={budget.id}
              className={`card ${
                isOver
                  ? 'border-l-4 border-red-500'
                  : isWarning
                  ? 'border-l-4 border-yellow-500'
                  : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Category header */}
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-2xl">
                      {getCategoryIcon(budget.category)}
                    </span>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {budget.category}
                      </h3>
                      <p className="text-sm text-gray-500 capitalize">
                        {budget.period} budget
                      </p>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">
                        {budget.spent.toFixed(0)} / {budget.amount.toFixed(0)} TND
                      </span>
                      <span
                        className={`text-sm font-semibold ${
                          isOver
                            ? 'text-red-600'
                            : isWarning
                            ? 'text-yellow-600'
                            : 'text-gray-900'
                        }`}
                      >
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${
                          isOver
                            ? 'bg-red-500'
                            : isWarning
                            ? 'bg-yellow-500'
                            : 'bg-primary-600'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Variance */}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Variance</span>
                    <span
                      className={`font-semibold ${
                        budget.variance > 0 ? 'text-red-600' : 'text-green-600'
                      }`}
                    >
                      {budget.variance > 0 ? '+' : ''}
                      {budget.variance.toFixed(0)} TND
                    </span>
                  </div>

                  {/* Warning message */}
                  {isOver && (
                    <div className="mt-3 p-3 bg-red-50 rounded-lg">
                      <p className="text-sm text-red-800">
                        ⚠️ Over budget by {(percentage - 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                  {isWarning && !isOver && (
                    <div className="mt-3 p-3 bg-yellow-50 rounded-lg">
                      <p className="text-sm text-yellow-800">
                        ⚠️ Approaching budget limit (
                        {budget.alert_threshold}% threshold)
                      </p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="ml-4 flex flex-col space-y-2">
                  <button className="btn-secondary text-sm px-3 py-1">
                    Edit
                  </button>
                  <button className="text-sm text-red-600 hover:text-red-800">
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
