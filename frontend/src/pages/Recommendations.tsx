import { useState, useEffect } from 'react';
import { 
  LightBulbIcon, 
  SparklesIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';
import { recommendationsService, type Recommendation } from '../services/recommendations';

export function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [totalSavings, setTotalSavings] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      const data = await recommendationsService.getAll();
      setRecommendations(data.recommendations);
      setTotalSavings(data.total_potential_savings);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupedRecommendations = recommendations.reduce((acc, rec) => {
    if (!acc[rec.type]) acc[rec.type] = [];
    acc[rec.type].push(rec);
    return acc;
  }, {} as Record<string, Recommendation[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
          <p className="mt-2 text-sm text-gray-500">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <SparklesIcon className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">AI Recommendations</h1>
        </div>
        <p className="text-gray-500">
          Personalized insights to improve your financial health
        </p>
      </div>

      {/* Potential Savings */}
      {totalSavings > 0 && (
        <div className="card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-green-500 rounded-2xl text-white">
              <ArrowTrendingDownIcon className="h-8 w-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-green-700">
                Total Potential Savings
              </p>
              <p className="text-3xl font-bold text-green-900 mt-1">
                {totalSavings.toFixed(0)} TND/month
              </p>
              <p className="text-sm text-green-600 mt-1">
                Follow these recommendations to save more
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations by Type */}
      {Object.entries(groupedRecommendations).map(([type, recs]) => (
        <div key={type}>
          <h2 className="text-lg font-semibold text-gray-900 mb-3 capitalize">
            {type.replace('_', ' ')}
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {recs.map((rec) => (
              <div
                key={rec.id}
                className={`card border-l-4 ${
                  rec.severity === 'critical'
                    ? 'border-red-500'
                    : rec.severity === 'warning'
                    ? 'border-yellow-500'
                    : 'border-blue-500'
                }`}
              >
                <h3 className="font-semibold text-gray-900 mb-2">
                  {rec.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {rec.description}
                </p>
                {rec.potential_savings > 0 && (
                  <div className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-semibold mb-3">
                    💰 Save {rec.potential_savings.toFixed(0)} TND/month
                  </div>
                )}
                {rec.action && (
                  <button className="text-sm font-medium text-primary-600 hover:text-primary-700 underline">
                    {rec.action} →
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {recommendations.length === 0 && (
        <div className="card text-center py-12">
          <LightBulbIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">No recommendations</p>
          <p className="text-sm text-gray-400 mt-1">
            You're doing great! Check back later for new insights.
          </p>
        </div>
      )}
    </div>
  );
}
