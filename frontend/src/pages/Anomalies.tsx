import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface Anomaly {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
  anomaly_score: number;
}

export function Anomalies() {
  const anomalies: Anomaly[] = [
    {
      id: '1',
      date: '2026-02-14',
      description: 'Large grocery purchase',
      amount: 5000,
      category: 'Groceries',
      severity: 'high',
      explanation: 'Amount is 66x your average Groceries spend (avg 75.66 TND)',
      anomaly_score: 1.0,
    },
    {
      id: '2',
      date: '2026-02-12',
      description: 'Unusual transport expense',
      amount: 850,
      category: 'Transport',
      severity: 'medium',
      explanation: 'Amount is 19x your average Transport spend (avg 45 TND)',
      anomaly_score: 0.65,
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Anomaly Detection</h1>
        <p className="mt-1 text-sm text-gray-500">
          AI-detected unusual transactions that may require attention
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-red-100">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High Severity</p>
              <p className="text-2xl font-bold text-gray-900">1</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-yellow-100">
              <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Medium Severity</p>
              <p className="text-2xl font-bold text-gray-900">1</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <ExclamationTriangleIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Low Severity</p>
              <p className="text-2xl font-bold text-gray-900">0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Anomalies list */}
      <div className="space-y-4">
        {anomalies.map((anomaly) => (
          <div
            key={anomaly.id}
            className={`card border-l-4 ${
              anomaly.severity === 'high'
                ? 'border-red-500'
                : anomaly.severity === 'medium'
                ? 'border-yellow-500'
                : 'border-blue-500'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${getSeverityColor(
                      anomaly.severity
                    )}`}
                  >
                    {anomaly.severity}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(anomaly.date).toLocaleDateString('en-GB')}
                  </span>
                </div>

                <h3 className="mt-2 text-lg font-semibold text-gray-900">
                  {anomaly.description}
                </h3>

                <p className="mt-1 text-sm text-gray-600">{anomaly.explanation}</p>

                <div className="mt-4 flex items-center space-x-6">
                  <div>
                    <p className="text-xs text-gray-500">Amount</p>
                    <p className="text-lg font-bold text-gray-900">
                      {anomaly.amount.toFixed(2)} TND
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Category</p>
                    <p className="text-sm font-medium text-gray-900">
                      {anomaly.category}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Anomaly Score</p>
                    <p className="text-sm font-medium text-gray-900">
                      {(anomaly.anomaly_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="ml-4">
                <button className="btn-secondary text-sm">Review</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
