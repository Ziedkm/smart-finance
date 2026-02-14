import { useState } from 'react';
import { PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { getCategoryIcon } from '../utils/categories';

interface Transaction {
  id: string;
  date: string;
  description: string;
  merchant: string;
  category: string;
  amount: number;
  type: 'income' | 'expense';
}

export function Transactions() {
  const [transactions] = useState<Transaction[]>([
    {
      id: '1',
      date: '2026-02-14',
      description: 'Weekly shopping',
      merchant: 'Carrefour',
      category: 'Groceries',
      amount: 85.50,
      type: 'expense',
    },
    {
      id: '2',
      date: '2026-02-13',
      description: 'Salary',
      merchant: 'ACME Corp',
      category: 'Income',
      amount: 4500,
      type: 'income',
    },
    {
      id: '3',
      date: '2026-02-13',
      description: 'Gas',
      merchant: 'Shell',
      category: 'Transport',
      amount: 45,
      type: 'expense',
    },
    {
      id: '4',
      date: '2026-02-12',
      description: 'Dinner',
      merchant: 'Pizza Hut',
      category: 'Dining',
      amount: 32,
      type: 'expense',
    },
    {
      id: '5',
      date: '2026-02-11',
      description: 'Electricity bill',
      merchant: 'STEG',
      category: 'Bills & Utilities',
      amount: 120,
      type: 'expense',
    },
  ]);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage and track all your financial transactions
          </p>
        </div>
        <button className="btn-primary flex items-center justify-center">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Transaction
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4">
          <button className="flex items-center justify-center sm:justify-start text-sm text-gray-600 hover:text-gray-900">
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
          <select className="input text-sm">
            <option>All Categories</option>
            <option>Groceries</option>
            <option>Transport</option>
            <option>Dining</option>
          </select>
          <select className="input text-sm">
            <option>Last 30 days</option>
            <option>Last 7 days</option>
            <option>This month</option>
            <option>Last month</option>
          </select>
        </div>
      </div>

      {/* Transactions list - mobile cards, desktop table */}
      <div className="card overflow-hidden p-0">
        {/* Desktop table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Category
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.map((transaction) => (
                <tr key={transaction.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(transaction.date).toLocaleDateString('en-GB')}
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {transaction.description}
                      </div>
                      <div className="text-sm text-gray-500">
                        {transaction.merchant}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {getCategoryIcon(transaction.category)} {transaction.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span
                      className={`text-sm font-semibold ${
                        transaction.type === 'income'
                          ? 'text-green-600'
                          : 'text-gray-900'
                      }`}
                    >
                      {transaction.type === 'income' ? '+' : '-'}
                      {transaction.amount.toFixed(2)} TND
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile cards */}
        <div className="md:hidden divide-y divide-gray-200">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {transaction.description}
                  </p>
                  <p className="text-xs text-gray-500">
                    {transaction.merchant}
                  </p>
                </div>
                <span
                  className={`text-sm font-semibold ${
                    transaction.type === 'income'
                      ? 'text-green-600'
                      : 'text-gray-900'
                  }`}
                >
                  {transaction.type === 'income' ? '+' : '-'}
                  {transaction.amount.toFixed(2)} TND
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {getCategoryIcon(transaction.category)} {transaction.category}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(transaction.date).toLocaleDateString('en-GB')}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
