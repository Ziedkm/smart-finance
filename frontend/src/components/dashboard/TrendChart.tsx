import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface TrendData {
  date: string;
  income: number;
  expenses: number;
}

interface TrendChartProps {
  data: TrendData[];
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Income vs Expenses Trend
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip formatter={(value: number) => `${value.toFixed(2)} TND`} />
          <Legend />
          <Line type="monotone" dataKey="income" stroke="#22c55e" strokeWidth={2} />
          <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
