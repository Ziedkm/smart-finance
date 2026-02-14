"""
AI Service - Integration with trained models
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from app.config import get_settings
from ai_modules.expense_classifier import ExpenseClassifier
from ai_modules.anomaly_detector import AnomalyDetector
from ai_modules.recommendation_engine import RecommendationEngine

try:
    from ai_modules.forecaster import FinancialForecaster  # Changed: correct class name
    FORECASTER_AVAILABLE = True
except ImportError as e:
    FORECASTER_AVAILABLE = False
    print(f"⚠️  Forecaster module not available - forecasting features disabled: {e}")

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
        
        # Optional forecaster
        if FORECASTER_AVAILABLE:
            self.forecaster = FinancialForecaster()  # Changed: correct class name
        else:
            self.forecaster = None
        
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
    
    def detect_anomaly(self, transaction, user_history):
        """
        Robust anomaly detection:
        - Uses simple statistics per category (reliable, deterministic)
        - Optionally can be combined with IsolationForest if you want
        """
        if not user_history or len(user_history) < 10:
            return None

        amount = float(transaction.get("amount", 0) or 0)
        category = transaction.get("category")

        # Filter comparable history (same type/category if available)
        hist = [t for t in user_history if t.get("transaction_type") == "expense"]
        if category:
            same_cat = [t for t in hist if t.get("category") == category]
            if len(same_cat) >= 5:
                hist = same_cat

        amounts = [float(t.get("amount", 0) or 0) for t in hist if t.get("amount") is not None]
        amounts = [a for a in amounts if a > 0]

        if len(amounts) < 5:
            return None

        avg = sum(amounts) / len(amounts)
        mx = max(amounts)
        # std (population)
        var = sum((a - avg) ** 2 for a in amounts) / len(amounts)
        std = var ** 0.5

        # Rules (tune these for your hackathon demo)
        z = 0.0 if std == 0 else (amount - avg) / std
        is_high_outlier = (amount > avg + 4 * std) or (amount > 3 * avg) or (amount > 1.5 * mx)
        is_low_outlier = (amount < avg - 4 * std) and (amount < 0.3 * avg)

        if not (is_high_outlier or is_low_outlier):
            return None

        # Score 0..1 (simple mapping)
        magnitude = max(abs(z) / 10.0, 0.0)
        anomaly_score = min(1.0, magnitude)

        explanation = (
            f"Amount {amount:.2f} is unusual vs your history "
            f"(avg {avg:.2f}, max {mx:.2f}, std {std:.2f}, z {z:.2f})"
        )

        return {
            "is_anomaly": True,
            "anomaly_score": anomaly_score,
            "severity": self._calculate_severity(anomaly_score),
            "explanation": explanation,
            "stats": {"count": len(amounts), "avg": avg, "max": mx, "std": std, "z": z},
        }


    
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
