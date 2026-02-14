export const CATEGORIES = [
  { id: '1', name: 'Groceries', icon: '🛒', color: '#10b981' },
  { id: '2', name: 'Transport', icon: '🚗', color: '#3b82f6' },
  { id: '3', name: 'Dining', icon: '🍽️', color: '#f59e0b' },
  { id: '4', name: 'Bills & Utilities', icon: '💡', color: '#ef4444' },
  { id: '5', name: 'Shopping', icon: '🛍️', color: '#8b5cf6' },
  { id: '6', name: 'Entertainment', icon: '🎬', color: '#ec4899' },
  { id: '7', name: 'Healthcare', icon: '⚕️', color: '#06b6d4' },
  { id: '8', name: 'Education', icon: '📚', color: '#14b8a6' },
  { id: '9', name: 'Income', icon: '💰', color: '#22c55e' },
  { id: '10', name: 'Other', icon: '📦', color: '#6b7280' },
];

export const getCategoryIcon = (category: string) => {
  return CATEGORIES.find(c => c.name === category)?.icon || '📦';
};

export const getCategoryColor = (category: string) => {
  return CATEGORIES.find(c => c.name === category)?.color || '#6b7280';
};
