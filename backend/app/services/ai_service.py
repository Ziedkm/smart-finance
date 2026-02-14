"""
AI Service - Integration with trained models
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from app.config import get_settings
from ai_modules.expense_classifier import ExpenseClassifier
from ai_modules.anomaly_detector import AnomalyDetector
from ai_modules.forecaster import Forecaster
from ai_modules.recommendation_engine import RecommendationEngine

settings = get_settings()


class AIService:
    """AI model integration service"""
    
    def __init__(self):
        # Load models
        self.classifier = ExpenseClassifier(
            model_path=settings.EXPENSE_CLASSIFIER_PATH
        )
        
        self.anomaly_detector = AnomalyDetector()
        if os.path.exists(settings.ANOMALY_DETECTOR_PATH):
            self.anomaly_detector.load_model(settings.ANOMALY_DETECTOR_PATH)
        
        self.forecaster = Forecaster()
        self.recommendation_engine = RecommendationEngine()
    
    def classify_transaction(
        self,
        description: str,
        merchant: str,
        amount: float,
        categories: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Classify transaction and return category suggestion
        
        Args:
            description: Transaction description
            merchant: Merchant name
            amount: Transaction amount
            categories: List of available categories [{id, name}]
            
        Returns:
            Classification result with confidence
        """
        # Get prediction from ML model
        prediction = self.classifier.predict(description, merchant, amount)
        
        # Map predicted category name to category ID
        category_map = {cat['name']: cat['id'] for cat in categories}
        predicted_name = prediction['category']
        category_id = category_map.get(predicted_name)
        
        # Get top 3 predictions with IDs
        top_3 = []
        for pred in prediction.get('top_3', []):
            cat_name = pred['category']
            cat_id = category_map.get(cat_name)
            if cat_id:
                top_3.append({
                    'category_id': cat_id,
                    'category_name': cat_name,
                    'confidence': pred['confidence']
                })
        
        return {
            'category_id': category_id,
            'category_name': predicted_name,
            'confidence': prediction['confidence'],
            'method': prediction['method'],
            'explanation': prediction.get('explanation', ''),
            'top_3_predictions': top_3
        }
    
    def detect_anomaly(
        self,
        transaction: Dict[str, Any],
        user_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if transaction is anomalous
        
        Args:
            transaction: Current transaction
            user_history: User's historical transactions
            
        Returns:
            Anomaly result if detected, None otherwise
        """
        # Combine current transaction with history
        all_transactions = user_history + [transaction]
        
        # Detect anomalies
        anomalies = self.anomaly_detector.batch_detect(all_transactions)
        
        # Check if current transaction is flagged
        current_txn_id = transaction.get('id')
        for anomaly in anomalies:
            if anomaly.get('id') == current_txn_id:
                return {
                    'is_anomaly': True,
                    'anomaly_score': anomaly.get('anomaly_score', 0.0),
                    'explanation': anomaly.get('explanation', 'Unusual transaction pattern'),
                    'severity': self._calculate_severity(anomaly.get('anomaly_score', 0.0))
                }
        
        return None
    
    def forecast_expenses(
        self,
        transactions: List[Dict[str, Any]],
        months_ahead: int = 3
    ) -> Dict[str, Any]:
        """
        Forecast future expenses
        
        Args:
            transactions: Historical transactions
            months_ahead: Number of months to forecast
            
        Returns:
            Forecast results
        """
        return self.forecaster.forecast(transactions, months_ahead)
    
    def generate_recommendations(
        self,
        user_id: str,
        budgets: List[Dict[str, Any]],
        goals: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations
        
        Args:
            user_id: User UUID
            budgets: User's budgets with variance
            goals: User's goals with progress
            transactions: Recent transactions
            anomalies: Pending anomalies
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Budget warnings
        for budget in budgets:
            if budget.get('status') == 'exceeded':
                recommendations.append({
                    'user_id': user_id,
                    'type': 'budget_warning',
                    'priority': 'urgent',
                    'title': f"Budget Exceeded: {budget['category_name']}",
                    'message': f"You've spent {budget['utilization_percent']:.0f}% of your {budget['category_name']} budget this month.",
                    'action_url': f"/budgets/{budget['id']}"
                })
            elif budget.get('status') == 'warning':
                recommendations.append({
                    'user_id': user_id,
                    'type': 'budget_warning',
                    'priority': 'high',
                    'title': f"Budget Warning: {budget['category_name']}",
                    'message': f"You're at {budget['utilization_percent']:.0f}% of your {budget['category_name']} budget.",
                    'action_url': f"/budgets/{budget['id']}"
                })
        
        # Goal suggestions
        for goal in goals:
            if not goal.get('on_track') and goal.get('status') == 'in_progress':
                recommendations.append({
                    'user_id': user_id,
                    'type': 'goal_suggestion',
                    'priority': 'medium',
                    'title': f"Goal Behind Schedule: {goal['name']}",
                    'message': f"Increase monthly contribution to {goal['required_monthly_contribution']:.2f} TND to stay on track.",
                    'action_url': f"/goals/{goal['id']}"
                })
        
        # Anomaly alerts
        for anomaly in anomalies:
            if anomaly.get('status') == 'pending':
                recommendations.append({
                    'user_id': user_id,
                    'type': 'anomaly_alert',
                    'priority': 'high',
                    'title': "Unusual Transaction Detected",
                    'message': anomaly.get('explanation', 'Please review this transaction'),
                    'action_url': f"/anomalies/{anomaly['id']}"
                })
        
        # Spending insights (from recommendation engine)
        insights = self.recommendation_engine.generate_recommendations({
            'budgets': budgets,
            'goals': goals,
            'transactions': transactions
        })
        
        for insight in insights:
            recommendations.append({
                'user_id': user_id,
                'type': insight.get('type', 'spending_insight'),
                'priority': insight.get('priority', 'low'),
                'title': insight.get('title'),
                'message': insight.get('message'),
                'action_url': insight.get('action_url')
            })
        
        return recommendations
    
    def _calculate_severity(self, anomaly_score: float) -> str:
        """Calculate anomaly severity from score"""
        if anomaly_score > 0.7:
            return 'high'
        elif anomaly_score > 0.4:
            return 'medium'
        else:
            return 'low'


# Singleton instance
_ai_service_instance = None


def get_ai_service() -> AIService:
    """Get cached AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
