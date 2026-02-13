"""
NLP Chatbot Module
- Intent recognition using keyword matching + fuzzy matching
- Template-based response generation with real KPI data
- Context-aware financial guidance
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from difflib import SequenceMatcher


class FinancialChatbot:
    """Conversational assistant for financial queries"""
    
    # Intent patterns (keyword-based for MVP)
    INTENT_PATTERNS = {
        'spending_summary': [
            r'\b(where|how much|what).*(money|spend|spent|spending)\b',
            r'\b(top|most|biggest).*(expense|category|spending)\b',
            r'\bmoney.*go\b',
            r'\bspending.*breakdown\b'
        ],
        'anomaly_explanation': [
            r'\b(why|what|explain).*(flag|flagged|anomaly|unusual|suspicious)\b',
            r'\b(this|that).*(transaction|purchase|charge)\b',
            r'\btransaction.*wrong\b'
        ],
        'goal_progress': [
            r'\b(how|when|can i).*(reach|achieve|hit|get to).*(goal|target)\b',
            r'\b(goal|target).*(progress|status|on track)\b',
            r'\bhow.*doing.*(goal|saving)\b'
        ],
        'budget_status': [
            r'\b(budget|budgets).*(status|remaining|left|how much)\b',
            r'\b(over|under|within).*budget\b',
            r'\bhow much.*(left|remaining).*budget\b'
        ],
        'recommendations': [
            r'\b(what|how).*(should|can).*(save|cut|reduce|improve)\b',
            r'\b(advice|recommendation|suggestion|tip).*\b',
            r'\b(help|ways).*(save money|reduce spending)\b'
        ],
        'trends': [
            r'\b(trend|pattern|change|comparison)\b',
            r'\b(last month|this month|compared to)\b',
            r'\b(increase|decrease|more|less).*spending\b'
        ],
        'category_detail': [
            r'\b(how much|what).*(category|groceries|transport|dining)\b',
            r'\bspending.*(groceries|transport|dining|shopping|bills)\b'
        ]
    }
    
    # Response templates
    RESPONSE_TEMPLATES = {
        'spending_summary': (
            "This month, you've spent **{total_expenses:.2f} TND** across {n_categories} categories. "
            "Your top spending areas are:\n\n"
            "1. **{cat1_name}**: {cat1_amount:.2f} TND ({cat1_percent:.0f}%)\n"
            "2. **{cat2_name}**: {cat2_amount:.2f} TND ({cat2_percent:.0f}%)\n"
            "3. **{cat3_name}**: {cat3_amount:.2f} TND ({cat3_percent:.0f}%)\n\n"
            "Your income was {total_income:.2f} TND, leaving you with a net of {net_amount:.2f} TND."
        ),
        'anomaly_explanation': (
            "The transaction of **{amount:.2f} TND** at {merchant} was flagged because:\n\n"
            "{explanation}\n\n"
            "For context:\n"
            "- Your average {category} transaction: {category_avg:.2f} TND\n"
            "- This transaction is {deviation:.1f}x your typical amount\n\n"
            "If this purchase was intentional, you can dismiss this alert."
        ),
        'goal_progress': (
            "Here's your progress on **{goal_name}**:\n\n"
            "- Target: {target_amount:.2f} TND by {target_date}\n"
            "- Current: {current_amount:.2f} TND ({completion_percent:.0f}% complete)\n"
            "- Remaining: {remaining_amount:.2f} TND\n\n"
            "{prediction_text}\n\n"
            "{advice_text}"
        ),
        'budget_status': (
            "Your budget status for this month:\n\n"
            "{budget_details}\n\n"
            "Overall, you've used {total_utilization:.0f}% of your total budget."
        ),
        'recommendations': (
            "Here are my top recommendations to improve your finances:\n\n"
            "{recommendations_list}\n\n"
            "Total potential savings: **{total_savings:.2f} TND per month**"
        ),
        'trends': (
            "Your spending trends:\n\n"
            "**This Month**: {current_month_total:.2f} TND\n"
            "**Last Month**: {previous_month_total:.2f} TND\n"
            "**Change**: {change_amount:+.2f} TND ({change_percent:+.0f}%)\n\n"
            "{trend_explanation}"
        ),
        'greeting': (
            "Hello! I'm your Smart Finance assistant. I can help you with:\n\n"
            "- 💰 Spending summaries and breakdowns\n"
            "- 🎯 Goal progress and predictions\n"
            "- 📊 Budget status and alerts\n"
            "- 💡 Personalized recommendations\n"
            "- 🔍 Anomaly explanations\n"
            "- 📈 Spending trends and patterns\n\n"
            "What would you like to know?"
        ),
        'fallback': (
            "I'm not sure I understood that. I can help you with:\n\n"
            "- \"Where did my money go?\"\n"
            "- \"Why was this transaction flagged?\"\n"
            "- \"How am I doing on my goals?\"\n"
            "- \"What's my budget status?\"\n"
            "- \"What should I cut to save money?\"\n"
            "- \"Show me spending trends\"\n\n"
            "Try asking one of these questions!"
        )
    }
    
    def __init__(self):
        self.conversation_history = []
    
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """
        Detect user intent from message
        
        Returns:
            (intent, confidence)
        """
        message_lower = message.lower().strip()
        
        # Check for greeting
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'help']):
            if len(message_lower.split()) <= 3:  # Short greeting
                return 'greeting', 0.95
        
        # Check each intent pattern
        best_match = ('unknown', 0.0)
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Calculate confidence based on pattern match quality
                    confidence = 0.85
                    if best_match[1] < confidence:
                        best_match = (intent, confidence)
        
        # If no pattern match, try fuzzy matching with common queries
        if best_match[0] == 'unknown':
            common_queries = {
                'spending_summary': ['where did my money go', 'what did i spend', 'spending breakdown'],
                'anomaly_explanation': ['why is this flagged', 'explain this transaction', 'why unusual'],
                'goal_progress': ['how is my goal', 'goal progress', 'will i reach my goal'],
                'recommendations': ['what should i cut', 'how to save', 'reduce spending']
            }
            
            for intent, queries in common_queries.items():
                for query in queries:
                    similarity = SequenceMatcher(None, message_lower, query).ratio()
                    if similarity > 0.6:
                        return intent, similarity
        
        return best_match
    
    def get_response(
        self,
        message: str,
        user_data: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate chatbot response
        
        Args:
            message: User's message
            user_data: Dict containing:
                - transactions: List[Dict]
                - budgets: List[Dict]
                - goals: List[Dict]
                - anomalies: List[Dict]
                - recommendations: List[Dict]
            context: Optional context (e.g., specific transaction ID)
            
        Returns:
            {
                'message': str,
                'intent': str,
                'confidence': float,
                'data': dict  # Supporting data for frontend
            }
        """
        # Detect intent
        intent, confidence = self.detect_intent(message)
        
        # Generate response based on intent
        if intent == 'greeting':
            return {
                'message': self.RESPONSE_TEMPLATES['greeting'],
                'intent': intent,
                'confidence': confidence,
                'data': {}
            }
        
        elif intent == 'spending_summary':
            return self._generate_spending_summary(user_data)
        
        elif intent == 'anomaly_explanation':
            return self._generate_anomaly_explanation(user_data, context)
        
        elif intent == 'goal_progress':
            return self._generate_goal_progress(user_data)
        
        elif intent == 'budget_status':
            return self._generate_budget_status(user_data)
        
        elif intent == 'recommendations':
            return self._generate_recommendations_response(user_data)
        
        elif intent == 'trends':
            return self._generate_trends_response(user_data)
        
        else:
            return {
                'message': self.RESPONSE_TEMPLATES['fallback'],
                'intent': 'unknown',
                'confidence': 0.0,
                'data': {}
            }
    
    def _generate_spending_summary(self, user_data: Dict) -> Dict:
        """Generate spending summary response"""
        transactions = user_data.get('transactions', [])
        
        # Filter current month expenses
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        current_month = datetime.now().replace(day=1)
        current_txns = df[df['transaction_date'] >= current_month]
        
        total_income = current_txns[current_txns['transaction_type'] == 'income']['amount'].sum()
        total_expenses = current_txns[current_txns['transaction_type'] == 'expense']['amount'].sum()
        net_amount = total_income - total_expenses
        
        # Get top categories
        category_totals = (
            current_txns[current_txns['transaction_type'] == 'expense']
            .groupby('category')['amount']
            .sum()
            .sort_values(ascending=False)
        )
        
        top_3 = []
        for i, (cat, amount) in enumerate(category_totals.head(3).items()):
            top_3.append({
                'name': cat,
                'amount': amount,
                'percent': (amount / total_expenses * 100) if total_expenses > 0 else 0
            })
        
        # Fill template
        response_data = {
            'total_expenses': total_expenses,
            'n_categories': len(category_totals),
            'total_income': total_income,
            'net_amount': net_amount,
            'cat1_name': top_3[0]['name'] if len(top_3) > 0 else 'N/A',
            'cat1_amount': top_3[0]['amount'] if len(top_3) > 0 else 0,
            'cat1_percent': top_3[0]['percent'] if len(top_3) > 0 else 0,
            'cat2_name': top_3[1]['name'] if len(top_3) > 1 else 'N/A',
            'cat2_amount': top_3[1]['amount'] if len(top_3) > 1 else 0,
            'cat2_percent': top_3[1]['percent'] if len(top_3) > 1 else 0,
            'cat3_name': top_3[2]['name'] if len(top_3) > 2 else 'N/A',
            'cat3_amount': top_3[2]['amount'] if len(top_3) > 2 else 0,
            'cat3_percent': top_3[2]['percent'] if len(top_3) > 2 else 0,
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['spending_summary'].format(**response_data),
            'intent': 'spending_summary',
            'confidence': 0.9,
            'data': response_data
        }
    
    def _generate_anomaly_explanation(self, user_data: Dict, context: Optional[Dict]) -> Dict:
        """Generate anomaly explanation response"""
        anomalies = user_data.get('anomalies', [])
        
        if not anomalies:
            return {
                'message': "You don't have any flagged transactions at the moment. Great job!",
                'intent': 'anomaly_explanation',
                'confidence': 0.9,
                'data': {}
            }
        
        # Get most recent or context-specified anomaly
        if context and context.get('anomaly_id'):
            anomaly = next((a for a in anomalies if a['id'] == context['anomaly_id']), anomalies[0])
        else:
            anomaly = anomalies[0]  # Most recent
        
        response_data = {
            'amount': anomaly.get('amount', 0),
            'merchant': anomaly.get('merchant', 'Unknown'),
            'explanation': anomaly.get('explanation', 'Unusual pattern detected'),
            'category': anomaly.get('category', 'Unknown'),
            'category_avg': anomaly.get('baseline_value', 0),
            'deviation': anomaly.get('amount', 0) / max(anomaly.get('baseline_value', 1), 1)
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['anomaly_explanation'].format(**response_data),
            'intent': 'anomaly_explanation',
            'confidence': 0.9,
            'data': response_data
        }
    
    def _generate_goal_progress(self, user_data: Dict) -> Dict:
        """Generate goal progress response"""
        goals = user_data.get('goals', [])
        
        if not goals:
            return {
                'message': "You haven't set any financial goals yet. Would you like to create one?",
                'intent': 'goal_progress',
                'confidence': 0.9,
                'data': {}
            }
        
        # Get first active goal
        active_goal = next((g for g in goals if g.get('status') == 'active'), goals[0])
        
        target = active_goal['target_amount']
        current = active_goal['current_amount']
        remaining = target - current
        completion = (current / target * 100) if target > 0 else 0
        
        # Generate prediction text
        if completion >= 100:
            prediction_text = "🎉 Congratulations! You've reached this goal!"
            advice_text = ""
        elif completion >= 75:
            prediction_text = "You're on track! Keep up the great work."
            advice_text = f"Just {remaining:.2f} TND more to go!"
        else:
            months_remaining = max(1, (pd.to_datetime(active_goal['target_date']) - datetime.now()).days / 30)
            required_monthly = remaining / months_remaining
            prediction_text = f"You need to save {required_monthly:.2f} TND per month to reach your goal on time."
            advice_text = "Consider reviewing your budget to find extra savings opportunities."
        
        response_data = {
            'goal_name': active_goal['name'],
            'target_amount': target,
            'current_amount': current,
            'target_date': pd.to_datetime(active_goal['target_date']).strftime('%B %Y'),
            'completion_percent': completion,
            'remaining_amount': remaining,
            'prediction_text': prediction_text,
            'advice_text': advice_text
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['goal_progress'].format(**response_data),
            'intent': 'goal_progress',
            'confidence': 0.9,
            'data': response_data
        }
    
    def _generate_budget_status(self, user_data: Dict) -> Dict:
        """Generate budget status response"""
        budgets = user_data.get('budgets', [])
        
        if not budgets:
            return {
                'message': "You haven't set up any budgets yet. Budgets help track your spending!",
                'intent': 'budget_status',
                'confidence': 0.9,
                'data': {}
            }
        
        budget_lines = []
        total_budget = 0
        total_spent = 0
        
        for budget in budgets:
            cat_name = budget['category_name']
            amount = budget['amount']
            actual = budget.get('actual_amount', 0)
            utilization = (actual / amount * 100) if amount > 0 else 0
            
            status_emoji = '🟢' if utilization < 80 else '🟡' if utilization < 100 else '🔴'
            budget_lines.append(
                f"{status_emoji} **{cat_name}**: {actual:.2f} / {amount:.2f} TND ({utilization:.0f}%)"
            )
            
            total_budget += amount
            total_spent += actual
        
        budget_details = '\n'.join(budget_lines)
        total_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        response_data = {
            'budget_details': budget_details,
            'total_utilization': total_utilization
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['budget_status'].format(**response_data),
            'intent': 'budget_status',
            'confidence': 0.9,
            'data': response_data
        }
    
    def _generate_recommendations_response(self, user_data: Dict) -> Dict:
        """Generate recommendations response"""
        recommendations = user_data.get('recommendations', [])
        
        if not recommendations:
            return {
                'message': "You're doing great! No major recommendations at the moment.",
                'intent': 'recommendations',
                'confidence': 0.9,
                'data': {}
            }
        
        rec_lines = []
        total_savings = 0
        
        for i, rec in enumerate(recommendations[:3], 1):
            savings = rec.get('estimated_monthly_savings', 0)
            rec_lines.append(
                f"{i}. **{rec['title']}**\n"
                f"   {rec['description']}\n"
                f"   💡 {rec['action_text']}\n"
                f"   💰 Potential savings: {savings:.2f} TND/month"
            )
            total_savings += savings
        
        recommendations_list = '\n\n'.join(rec_lines)
        
        response_data = {
            'recommendations_list': recommendations_list,
            'total_savings': total_savings
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['recommendations'].format(**response_data),
            'intent': 'recommendations',
            'confidence': 0.9,
            'data': response_data
        }
    
    def _generate_trends_response(self, user_data: Dict) -> Dict:
        """Generate trends response"""
        transactions = user_data.get('transactions', [])
        
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df[df['transaction_type'] == 'expense']
        
        current_month = datetime.now().replace(day=1)
        previous_month = (current_month - pd.DateOffset(months=1))
        
        current_total = df[df['transaction_date'] >= current_month]['amount'].sum()
        previous_total = df[
            (df['transaction_date'] >= previous_month) & 
            (df['transaction_date'] < current_month)
        ]['amount'].sum()
        
        change_amount = current_total - previous_total
        change_percent = (change_amount / previous_total * 100) if previous_total > 0 else 0
        
        if change_percent > 10:
            trend_explanation = "Your spending increased this month. Consider reviewing your recent purchases."
        elif change_percent < -10:
            trend_explanation = "Great job! You've reduced your spending this month."
        else:
            trend_explanation = "Your spending is stable compared to last month."
        
        response_data = {
            'current_month_total': current_total,
            'previous_month_total': previous_total,
            'change_amount': change_amount,
            'change_percent': change_percent,
            'trend_explanation': trend_explanation
        }
        
        return {
            'message': self.RESPONSE_TEMPLATES['trends'].format(**response_data),
            'intent': 'trends',
            'confidence': 0.9,
            'data': response_data
        }


# Example usage
if __name__ == "__main__":
    chatbot = FinancialChatbot()
    
    # Demo user data
    demo_data = {
        'transactions': [
            {'transaction_date': '2026-02-10', 'amount': 500, 'category': 'Groceries', 'transaction_type': 'expense'},
            {'transaction_date': '2026-02-12', 'amount': 300, 'category': 'Dining', 'transaction_type': 'expense'},
            {'transaction_date': '2026-02-05', 'amount': 3000, 'category': 'Income', 'transaction_type': 'income'},
        ],
        'goals': [],
        'budgets': [],
        'anomalies': [],
        'recommendations': []
    }
    
    # Test queries
    queries = [
        "Where did my money go this month?",
        "How am I doing on my goals?",
        "What should I cut to save money?"
    ]
    
    for query in queries:
        response = chatbot.get_response(query, demo_data)
        print(f"\nUser: {query}")
        print(f"Bot ({response['intent']}, {response['confidence']:.0%}):")
        print(response['message'])
        print("-" * 50)
