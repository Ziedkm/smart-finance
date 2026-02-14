import { useState, useEffect, useRef } from 'react';
import { 
  XMarkIcon, 
  ExclamationTriangleIcon, 
  LightBulbIcon, 
  ChartBarIcon,
  FlagIcon,
  ShieldExclamationIcon,
} from '@heroicons/react/24/outline';
import { recommendationsService, type Recommendation } from '../../services/recommendations';


interface NotificationsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function NotificationsPanel({ isOpen, onClose }: NotificationsPanelProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [totalSavings, setTotalSavings] = useState(0);
  const [loading, setLoading] = useState(true);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      loadRecommendations();
    }
  }, [isOpen]);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const data = await recommendationsService.getAll();
      setRecommendations(data.recommendations);
      setTotalSavings(data.total_potential_savings);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      await recommendationsService.dismiss(id);
      setRecommendations(prev => prev.filter(r => r.id !== id));
    } catch (error) {
      console.error('Failed to dismiss recommendation:', error);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'budget_alert':
        return ExclamationTriangleIcon;
      case 'savings_tip':
        return LightBulbIcon;
      case 'spending_insight':
        return ChartBarIcon;
      case 'goal_tip':
        return FlagIcon;
      case 'anomaly':
        return ShieldExclamationIcon;
      default:
        return LightBulbIcon;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700';
      case 'info':
        return 'bg-blue-50 border-blue-200 text-blue-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const getIconColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-500';
      case 'warning':
        return 'text-yellow-500';
      case 'info':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity" />

      {/* Panel */}
      <div className="absolute inset-y-0 right-0 flex max-w-full pl-10">
        <div
          ref={panelRef}
          className="w-screen max-w-md transform transition-all"
        >
          <div className="flex h-full flex-col bg-white shadow-2xl">
            {/* Header */}
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Notifications</h2>
                  <p className="text-sm text-primary-100 mt-1">
                    {recommendations.length} insights for you
                  </p>
                </div>
                <button
                  onClick={onClose}
                  className="rounded-lg p-2 hover:bg-white/10 transition-colors"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              {/* Potential Savings */}
              {totalSavings > 0 && (
                <div className="mt-4 rounded-xl bg-white/10 backdrop-blur-sm px-4 py-3 border border-white/20">
                  <p className="text-xs text-primary-100">Potential Monthly Savings</p>
                  <p className="text-2xl font-bold mt-1">{totalSavings.toFixed(0)} TND</p>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
                    <p className="mt-2 text-sm text-gray-500">Loading insights...</p>
                  </div>
                </div>
              ) : recommendations.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <LightBulbIcon className="h-16 w-16 text-gray-300 mb-4" />
                  <p className="text-gray-500 font-medium">No notifications</p>
                  <p className="text-sm text-gray-400 mt-1">You're all caught up!</p>
                </div>
              ) : (
                recommendations.map((recommendation) => {
                  const Icon = getIcon(recommendation.type);
                  const colorClass = getSeverityColor(recommendation.severity);
                  const iconColor = getIconColor(recommendation.severity);

                  return (
                    <div
                      key={recommendation.id}
                      className={`rounded-xl border-2 p-4 transition-all hover:shadow-md ${colorClass}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg bg-white/50 ${iconColor}`}>
                          <Icon className="h-5 w-5" />
                        </div>

                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm mb-1">
                            {recommendation.title}
                          </h3>
                          <p className="text-xs opacity-90 mb-2">
                            {recommendation.description}
                          </p>

                          {recommendation.potential_savings > 0 && (
                            <div className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold mb-2">
                              💰 Save {recommendation.potential_savings.toFixed(0)} TND/month
                            </div>
                          )}

                          {recommendation.action && (
                            <div className="flex items-center gap-2 mt-2">
                              <button className="text-xs font-medium underline hover:no-underline">
                                {recommendation.action}
                              </button>
                            </div>
                          )}
                        </div>

                        <button
                          onClick={() => handleDismiss(recommendation.id)}
                          className="p-1 hover:bg-white/50 rounded transition-colors"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
