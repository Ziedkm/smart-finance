"""
Recommendation Engine
- Rule-based + BI-driven recommendations
- Budget optimization suggestions
- Subscription detection and cancellation advice
- Spending reduction recommendations with savings estimates
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class RecommendationEngine:
    """Generate personalized financial recommendations"""
    
    def __init__(self):
        self.recommendation_priority = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
    
    def generate_recommendations(
        self,
        user_id: str,
        transactions: List[Dict],
        budgets: List[Dict],
        goals: List[Dict],
        profile: Dict
    ) -> List[Dict]:
        """
        Generate all recommendations for a user
        
        Returns:
            List of recommendation dicts sorted by priority
        """
        recommendations = []
        
        # 1. Budget overspending recommendations
        recommendations.extend(
            self._check_budget_overspending(transactions, budgets)
        )
        
        # 2. Subscription recommendations
        recommendations.extend(
            self._detect_subscriptions(transactions)
        )
        
        # 3. Category spending trends
        recommendations.extend(
            self._analyze_spending_trends(transactions)
        )
        
        # 4. Goal achievement recommendations
        recommendations.extend(
            self._goal_recommendations(transactions, goals, profile)
        )
        
        # 5. Savings opportunities
        recommendations.extend(
            self._find_savings_opportunities(transactions, profile)
        )
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: (
            self.recommendation_priority[x['priority']],
            -x['estimated_monthly_savings']
        ))
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _check_budget_overspending(
        self,
        transactions: List[Dict],
        budgets: List[Dict]
    ) -> List[Dict]:
        """Check for budget overspending and generate alerts"""
        recommendations = []
        
        # Get current month transactions
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_txns = [
            t for t in transactions
            if pd.to_datetime(t['transaction_date']) >= current_month_start
            and t['transaction_type'] == 'expense'
        ]
        
        # Calculate spending by category
        spending_by_category = defaultdict(float)
        for txn in current_month_txns:
            spending_by_category[txn['category']] += txn['amount']
        
        # Check against budgets
        for budget in budgets:
            if not budget.get('is_active'):
                continue
            
            category = budget['category_name']
            budget_amount = budget['amount']
            actual_amount = spending_by_category.get(category, 0)
            
            utilization = (actual_amount / budget_amount) * 100 if budget_amount > 0 else 0
            
            if utilization > 100:
                # Exceeded budget
                overspend = actual_amount - budget_amount
                reduction_target = overspend * 1.2  # Aim to reduce by 20% more as buffer
                
                recommendations.append({
                    'recommendation_type': 'reduce_spending',
                    'category': category,
                    'title': f'Budget Exceeded: {category}',
                    'description': (
                        f'You have spent {actual_amount:.2f} TND in {category}, '
                        f'which is {utilization:.0f}% of your {budget_amount:.2f} TND budget '
                        f'({overspend:.2f} TND over budget).'
                    ),
                    'action_text': f'Reduce {category} spending by {reduction_target:.2f} TND next month',
                    'estimated_monthly_savings': reduction_target,
                    'priority': 'high',
                    'supporting_data': {
                        'budget_amount': budget_amount,
                        'actual_amount': actual_amount,
                        'overspend': overspend,
                        'utilization_percent': utilization
                    }
                })
            
            elif utilization > 80:
                # Warning threshold
                remaining = budget_amount - actual_amount
                
                recommendations.append({
                    'recommendation_type': 'category_alert',
                    'category': category,
                    'title': f'Approaching Budget Limit: {category}',
                    'description': (
                        f'You have used {utilization:.0f}% of your {category} budget. '
                        f'Only {remaining:.2f} TND remaining for this month.'
                    ),
                    'action_text': f'Monitor {category} spending carefully',
                    'estimated_monthly_savings': 0,
                    'priority': 'medium',
                    'supporting_data': {
                        'budget_amount': budget_amount,
                        'actual_amount': actual_amount,
                        'remaining': remaining,
                        'utilization_percent': utilization
                    }
                })
        
        return recommendations
    
    def _detect_subscriptions(self, transactions: List[Dict]) -> List[Dict]:
        """Detect recurring subscriptions and suggest cancellations"""
        recommendations = []
        
        # Look for recurring patterns (same merchant, similar amount, ~monthly)
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df[df['transaction_type'] == 'expense'].copy()
        
        # Group by merchant
        merchant_groups = df.groupby('merchant')
        
        for merchant, group in merchant_groups:
            if len(group) < 2 or not merchant:
                continue
            
            # Check if amounts are similar (within 10% variance)
            amounts = group['amount'].values
            mean_amount = amounts.mean()
            std_amount = amounts.std()
            
            if std_amount / mean_amount < 0.1:  # Low variance = recurring
                # Check time intervals
                dates = group['transaction_date'].sort_values()
                intervals = dates.diff().dt.days.dropna()
                
                if len(intervals) > 0:
                    avg_interval = intervals.mean()
                    
                    # Monthly subscription (~30 days)
                    if 25 <= avg_interval <= 35:
                        last_txn_date = dates.max()
                        days_since_last = (datetime.now() - last_txn_date).days
                        
                        # If last transaction was recent, it's active
                        if days_since_last < 45:
                            recommendations.append({
                                'recommendation_type': 'cancel_subscription',
                                'category': group['category'].iloc[0],
                                'title': f'Active Subscription Detected: {merchant}',
                                'description': (
                                    f'You have a recurring monthly charge of {mean_amount:.2f} TND '
                                    f'to {merchant}. Consider if you still need this subscription.'
                                ),
                                'action_text': f'Review and potentially cancel to save {mean_amount:.2f} TND/month',
                                'estimated_monthly_savings': mean_amount,
                                'priority': 'medium',
                                'supporting_data': {
                                    'merchant': merchant,
                                    'amount': mean_amount,
                                    'frequency': 'monthly',
                                    'transaction_count': len(group),
                                    'last_transaction': str(last_txn_date.date())
                                }
                            })
        
        return recommendations
    
    def _analyze_spending_trends(self, transactions: List[Dict]) -> List[Dict]:
        """Analyze month-over-month spending trends"""
        recommendations = []
        
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df[df['transaction_type'] == 'expense'].copy()
        
        # Get last 2 months
        current_month = datetime.now().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_txns = df[df['transaction_date'] >= current_month]
        previous_txns = df[
            (df['transaction_date'] >= previous_month) &
            (df['transaction_date'] < current_month)
        ]
        
        # Compare by category
        current_by_cat = current_txns.groupby('category')['amount'].sum()
        previous_by_cat = previous_txns.groupby('category')['amount'].sum()
        
        for category in current_by_cat.index:
            current_amount = current_by_cat[category]
            previous_amount = previous_by_cat.get(category, 0)
            
            if previous_amount > 0:
                change_percent = ((current_amount - previous_amount) / previous_amount) * 100
                
                # Significant increase (>25%)
                if change_percent > 25:
                    increase_amount = current_amount - previous_amount
                    
                    recommendations.append({
                        'recommendation_type': 'reduce_spending',
                        'category': category,
                        'title': f'Spending Increase Alert: {category}',
                        'description': (
                            f'Your {category} spending increased by {change_percent:.0f}% '
                            f'this month ({current_amount:.2f} TND vs {previous_amount:.2f} TND last month). '
                            f'That\'s an increase of {increase_amount:.2f} TND.'
                        ),
                        'action_text': f'Reduce {category} spending back to previous levels',
                        'estimated_monthly_savings': increase_amount * 0.7,  # Aim to recover 70%
                        'priority': 'medium',
                        'supporting_data': {
                            'current_month_amount': current_amount,
                            'previous_month_amount': previous_amount,
                            'change_percent': change_percent,
                            'change_amount': increase_amount
                        }
                    })
        
        return recommendations
    
    def _goal_recommendations(
        self,
        transactions: List[Dict],
        goals: List[Dict],
        profile: Dict
    ) -> List[Dict]:
        """Generate recommendations for goal achievement"""
        recommendations = []
        
        # Calculate current monthly savings
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        current_month = datetime.now().replace(day=1)
        current_txns = df[df['transaction_date'] >= current_month]
        
        income = current_txns[current_txns['transaction_type'] == 'income']['amount'].sum()
        expenses = current_txns[current_txns['transaction_type'] == 'expense']['amount'].sum()
        current_savings = income - expenses
        
        for goal in goals:
            if goal.get('status') != 'active':
                continue
            
            target_amount = goal['target_amount']
            current_amount = goal['current_amount']
            remaining = target_amount - current_amount
            
            target_date = pd.to_datetime(goal['target_date'])
            months_remaining = max(1, (target_date - datetime.now()).days / 30)
            
            required_monthly = remaining / months_remaining
            
            # If current savings insufficient
            if current_savings < required_monthly:
                shortfall = required_monthly - current_savings
                
                recommendations.append({
                    'recommendation_type': 'increase_savings',
                    'category': None,
                    'title': f'Goal at Risk: {goal["name"]}',
                    'description': (
                        f'To reach your goal of {target_amount:.2f} TND by '
                        f'{target_date.strftime("%B %Y")}, you need to save '
                        f'{required_monthly:.2f} TND per month. Currently saving '
                        f'{current_savings:.2f} TND per month.'
                    ),
                    'action_text': f'Increase monthly savings by {shortfall:.2f} TND',
                    'estimated_monthly_savings': -shortfall,  # Negative = need to save more
                    'priority': 'high',
                    'supporting_data': {
                        'goal_name': goal['name'],
                        'target_amount': target_amount,
                        'current_amount': current_amount,
                        'required_monthly': required_monthly,
                        'current_monthly_savings': current_savings,
                        'shortfall': shortfall,
                        'months_remaining': months_remaining
                    }
                })
        
        return recommendations
    
    def _find_savings_opportunities(
        self,
        transactions: List[Dict],
        profile: Dict
    ) -> List[Dict]:
        """Find general savings opportunities"""
        recommendations = []
        
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df[df['transaction_type'] == 'expense'].copy()
        
        # Get current month
        current_month = datetime.now().replace(day=1)
        current_txns = df[df['transaction_date'] >= current_month]
        
        # Check for frequent small transactions in discretionary categories
        discretionary_categories = ['Dining', 'Entertainment', 'Shopping']
        
        for category in discretionary_categories:
            cat_txns = current_txns[current_txns['category'] == category]
            
            if len(cat_txns) > 10:  # Many small transactions
                total_spent = cat_txns['amount'].sum()
                avg_transaction = cat_txns['amount'].mean()
                
                # If spending on many small purchases
                if avg_transaction < 50 and total_spent > 200:
                    potential_savings = total_spent * 0.30  # Could save 30%
                    
                    recommendations.append({
                        'recommendation_type': 'reduce_spending',
                        'category': category,
                        'title': f'Frequent Small Purchases: {category}',
                        'description': (
                            f'You made {len(cat_txns)} {category} transactions this month '
                            f'(avg {avg_transaction:.2f} TND each), totaling {total_spent:.2f} TND. '
                            f'Consider reducing frequency of discretionary purchases.'
                        ),
                        'action_text': f'Reduce {category} frequency to save ~{potential_savings:.2f} TND/month',
                        'estimated_monthly_savings': potential_savings,
                        'priority': 'low',
                        'supporting_data': {
                            'transaction_count': len(cat_txns),
                            'total_spent': total_spent,
                            'avg_transaction': avg_transaction
                        }
                    })
        
        return recommendations
    
    def format_recommendation_for_db(self, recommendation: Dict, user_id: str) -> Dict:
        """Format recommendation for database insertion"""
        return {
            'user_id': user_id,
            'recommendation_type': recommendation['recommendation_type'],
            'category_id': None,  # Would need to look up category ID
            'title': recommendation['title'],
            'description': recommendation['description'],
            'action_text': recommendation['action_text'],
            'estimated_monthly_savings': recommendation['estimated_monthly_savings'],
            'priority': self.recommendation_priority[recommendation['priority']],
            'supporting_data': recommendation['supporting_data'],
            'status': 'active'
        }


# Example usage
if __name__ == "__main__":
    from datetime import date
    
    # Demo data
    demo_transactions = [
        {'transaction_date': date(2026, 2, 1), 'amount': 600, 'category': 'Groceries', 'transaction_type': 'expense', 'merchant': 'Carrefour'},
        {'transaction_date': date(2026, 2, 5), 'amount': 450, 'category': 'Dining', 'transaction_type': 'expense', 'merchant': 'Restaurant'},
        {'transaction_date': date(2026, 2, 10), 'amount': 9.99, 'category': 'Entertainment', 'transaction_type': 'expense', 'merchant': 'Netflix'},
        {'transaction_date': date(2026, 1, 10), 'amount': 9.99, 'category': 'Entertainment', 'transaction_type': 'expense', 'merchant': 'Netflix'},
        {'transaction_date': date(2025, 12, 10), 'amount': 9.99, 'category': 'Entertainment', 'transaction_type': 'expense', 'merchant': 'Netflix'},
    ]
    
    demo_budgets = [
        {'category_name': 'Groceries', 'amount': 500, 'is_active': True},
        {'category_name': 'Dining', 'amount': 300, 'is_active': True},
    ]
    
    demo_goals = [
        {
            'name': 'Vacation Fund',
            'target_amount': 5000,
            'current_amount': 2000,
            'target_date': date(2026, 8, 1),
            'status': 'active'
        }
    ]
    
    demo_profile = {'monthly_income': 3000}
    
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        'user_123',
        demo_transactions,
        demo_budgets,
        demo_goals,
        demo_profile
    )
    
    print(f"Generated {len(recommendations)} recommendations:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Savings: {rec['estimated_monthly_savings']:.2f} TND/month")
        print(f"   {rec['description']}\n")
