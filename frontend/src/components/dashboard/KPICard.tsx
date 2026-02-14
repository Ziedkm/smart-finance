interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
}

export function KPICard({ title, value, subtitle, trend, icon }: KPICardProps) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs sm:text-sm font-medium text-gray-600 truncate">{title}</p>
          <p className="mt-2 text-2xl sm:text-3xl font-bold text-gray-900 truncate">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs sm:text-sm text-gray-500 truncate">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center">
              <span
                className={`text-xs sm:text-sm font-medium ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="ml-2 text-xs text-gray-500">vs last month</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="ml-2 sm:ml-4 flex-shrink-0">
            <div className="rounded-lg bg-primary-50 p-2 sm:p-3 text-primary-600">
              {icon}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
