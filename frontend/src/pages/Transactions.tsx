import { useState, useMemo } from 'react';
import { PlusIcon, FunnelIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { getCategoryIcon } from '../utils/categories';
import { AddTransactionModal } from '../components/transactions/AddTransactionModal';

interface Transaction {
  id: string;
  date: string;
  description: string;
  merchant: string;
  category: string;
  amount: number;
  type: 'income' | 'expense';
}

const initialTransactions: Transaction[] = [
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
  {
    id: '6',
    date: '2026-02-10',
    description: 'Movie tickets',
    merchant: 'Pathé',
    category: 'Entertainment',
    amount: 24,
    type: 'expense',
  },
  {
    id: '7',
    date: '2026-02-09',
    description: 'Freelance project',
    merchant: 'Client XYZ',
    category: 'Income',
    amount: 800,
    type: 'income',
  },
  {
    id: '8',
    date: '2026-02-08',
    description: 'Pharmacy',
    merchant: 'Pharmacie Centrale',
    category: 'Healthcare',
    amount: 45,
    type: 'expense',
  },
];

export function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>(initialTransactions);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState<'all' | 'income' | 'expense'>('all');
  const [dateRange, setDateRange] = useState('all');

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(transactions.map(t => t.category));
    return ['all', ...Array.from(cats)];
  }, [transactions]);

  // Filter transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter(transaction => {
      // Search filter
      const matchesSearch = 
        transaction.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        transaction.merchant.toLowerCase().includes(searchQuery.toLowerCase());

      // Category filter
      const matchesCategory = selectedCategory === 'all' || transaction.category === selectedCategory;

      // Type filter
      const matchesType = selectedType === 'all' || transaction.type === selectedType;

      // Date range filter
      let matchesDate = true;
      if (dateRange !== 'all') {
        const transactionDate = new Date(transaction.date);
        const now = new Date();
        
        if (dateRange === 'today') {
          matchesDate = transactionDate.toDateString() === now.toDateString();
        } else if (dateRange === '7days') {
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          matchesDate = transactionDate >= weekAgo;
        } else if (dateRange === '30days') {
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          matchesDate = transactionDate >= monthAgo;
        } else if (dateRange === 'thisMonth') {
          matchesDate = 
            transactionDate.getMonth() === now.getMonth() &&
            transactionDate.getFullYear() === now.getFullYear();
        }
      }

      return matchesSearch && matchesCategory && matchesType && matchesDate;
    });
  }, [transactions, searchQuery, selectedCategory, selectedType, dateRange]);

  // Calculate totals
  const totals = useMemo(() => {
    return filteredTransactions.reduce(
      (acc, t) => {
        if (t.type === 'income') {
          acc.income += t.amount;
        } else {
          acc.expenses += t.amount;
        }
        return acc;
      },
      { income: 0, expenses: 0 }
    );
  }, [filteredTransactions]);

  const handleAddTransaction = (transaction: Transaction) => {
    setTransactions(prev => [transaction, ...prev]);
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedType('all');
    setDateRange('all');
  };

  const hasActiveFilters = searchQuery || selectedCategory !== 'all' || selectedType !== 'all' || dateRange !== 'all';

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="mt-1 text-sm text-gray-500">
            {filteredTransactions.length} of {transactions.length} transactions
          </p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center justify-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add Transaction
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <p className="text-sm font-medium text-green-700">Total Income</p>
          <p className="text-2xl font-bold text-green-900 mt-1">
            {totals.income.toFixed(2)} TND
          </p>
        </div>
        <div className="card bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <p className="text-sm font-medium text-red-700">Total Expenses</p>
          <p className="text-2xl font-bold text-red-900 mt-1">
            {totals.expenses.toFixed(2)} TND
          </p>
        </div>
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <p className="text-sm font-medium text-blue-700">Net Balance</p>
          <p className="text-2xl font-bold text-blue-900 mt-1">
            {(totals.income - totals.expenses).toFixed(2)} TND
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <FunnelIcon className="h-5 w-5 text-gray-500" />
          <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="ml-auto text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear all
            </button>
          )}
        </div>

        <div className="space-y-3">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transactions..."
              className="input pl-10"
            />
          </div>

          {/* Filter row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Category filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input text-sm"
            >
              <option value="all">All Categories</option>
              {categories.filter(c => c !== 'all').map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>

            {/* Type filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as any)}
              className="input text-sm"
            >
              <option value="all">All Types</option>
              <option value="income">Income</option>
              <option value="expense">Expenses</option>
            </select>

            {/* Date range filter */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="input text-sm"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="7days">Last 7 days</option>
              <option value="30days">Last 30 days</option>
              <option value="thisMonth">This month</option>
            </select>
          </div>
        </div>
      </div>

      {/* Transactions list */}
      {filteredTransactions.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No transactions found</p>
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              className="mt-4 text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
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
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50 transition-colors">
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
            {filteredTransactions.map((transaction) => (
              <div key={transaction.id} className="p-4 hover:bg-gray-50 transition-colors">
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
      )}

      {/* Add Transaction Modal */}
      <AddTransactionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddTransaction}
      />
    </div>
  );
}
