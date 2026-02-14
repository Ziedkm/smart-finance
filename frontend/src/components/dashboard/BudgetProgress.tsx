interface BudgetItem {
  category: string;
  spent: number;
  budget: number;
  variance: number;
}

interface BudgetProgressProps {
  budgets: BudgetItem[];
}

export function BudgetProgress({ budgets }: BudgetProgressProps) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Budget vs Actual
      </h3>
      <div className="space-y-4">
        {budgets.map((budget) => {
          const percentage = (budget.spent / budget.budget) * 100;
          const isOver = percentage > 100;
          
          return (
            <div key={budget.category}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">
                  {budget.category}
                </span>
                <span className={`text-sm font-semibold ${
                  isOver ? 'text-red-600' : 'text-gray-900'
                }`}>
                  {budget.spent.toFixed(0)} / {budget.budget.toFixed(0)} TND
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    isOver ? 'bg-red-500' : 'bg-primary-600'
                  }`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-xs text-gray-500">
                  {percentage.toFixed(0)}%
                </span>
                {budget.variance !== 0 && (
                  <span className={`text-xs font-medium ${
                    budget.variance > 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {budget.variance > 0 ? '+' : ''}{budget.variance.toFixed(0)} TND
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
