import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { getCategoryColor } from '../../utils/categories';

interface CategoryData {
  category: string;
  amount: number;
  percentage: number;
}

interface CategoryChartProps {
  data: CategoryData[];
}

export function CategoryChart({ data }: CategoryChartProps) {
  return (
    <div className="card">
      <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">
        Spending by Category
      </h3>
      <ResponsiveContainer width="100%" height={250} className="sm:h-[300px]">
        <PieChart>
          <Pie
            data={data}
            dataKey="amount"
            nameKey="category"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label={({ percentage }) => `${percentage.toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getCategoryColor(entry.category)} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `${value.toFixed(2)} TND`} />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
