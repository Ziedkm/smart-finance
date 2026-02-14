"""
AI Recommendations API
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.dependencies import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class Recommendation(BaseModel):
    id: str
    type: str  # budget_alert, savings_tip, spending_insight, goal_tip, anomaly
    title: str
    description: str
    severity: str  # info, warning, critical
    category: str
    potential_savings: float = 0
    action: str = ""
    created_at: str


class RecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]
    total_potential_savings: float


def generate_recommendations(user_data: Dict[str, Any]) -> List[Recommendation]:
    """Generate AI-powered recommendations based on user data"""
    recommendations = []
    
    # Budget Alerts
    for budget in user_data.get("budgets", []):
        if budget["spent"] > budget["budget"]:
            over_amount = budget["spent"] - budget["budget"]
            recommendations.append(Recommendation(
                id=f"budget_alert_{budget['category']}",
                type="budget_alert",
                title=f"Over Budget: {budget['category']}",
                description=f"You've exceeded your {budget['category']} budget by {over_amount:.0f} TND ({((over_amount/budget['budget'])*100):.1f}% over).",
                severity="critical",
                category=budget['category'],
                potential_savings=over_amount,
                action="Reduce spending or adjust budget",
                created_at=datetime.now().isoformat()
            ))
        elif budget["spent"] >= budget["budget"] * 0.8:
            remaining = budget["budget"] - budget["spent"]
            recommendations.append(Recommendation(
                id=f"budget_warning_{budget['category']}",
                type="budget_alert",
                title=f"Budget Alert: {budget['category']}",
                description=f"You've used 80% of your {budget['category']} budget. Only {remaining:.0f} TND remaining.",
                severity="warning",
                category=budget['category'],
                potential_savings=0,
                action="Monitor spending carefully",
                created_at=datetime.now().isoformat()
            ))
    
    # Spending Insights
    top_category = user_data.get("top_category", {})
    if top_category.get("percentage", 0) > 30:
        recommendations.append(Recommendation(
            id="spending_concentration",
            type="spending_insight",
            title="High Spending Concentration",
            description=f"{top_category['name']} accounts for {top_category['percentage']:.1f}% of your expenses. Consider diversifying spending or finding ways to reduce costs in this category.",
            severity="info",
            category=top_category['name'],
            potential_savings=top_category['amount'] * 0.2,
            action="Review and optimize spending",
            created_at=datetime.now().isoformat()
        ))
    
    # Savings Opportunities
    if user_data.get("savings_rate", 0) < 20:
        income = user_data.get("total_income", 0)
        current_savings = user_data.get("net_savings", 0)
        target_savings = income * 0.2
        potential = target_savings - current_savings
        
        recommendations.append(Recommendation(
            id="low_savings_rate",
            type="savings_tip",
            title="Low Savings Rate",
            description=f"Your current savings rate is {user_data.get('savings_rate', 0):.1f}%. Financial experts recommend saving at least 20% of income. You could save an additional {potential:.0f} TND per month.",
            severity="warning",
            category="Savings",
            potential_savings=potential,
            action="Increase automatic savings transfers",
            created_at=datetime.now().isoformat()
        ))
    
    # Goal Recommendations
    at_risk_goals = user_data.get("at_risk_goals", [])
    if at_risk_goals:
        recommendations.append(Recommendation(
            id="goals_at_risk",
            type="goal_tip",
            title="Goals Need Attention",
            description=f"You have {len(at_risk_goals)} goal(s) at risk of missing deadlines. Consider increasing monthly contributions or adjusting target dates.",
            severity="warning",
            category="Goals",
            potential_savings=0,
            action="Review goal progress",
            created_at=datetime.now().isoformat()
        ))
    
    # Anomaly Alerts
    anomaly_count = user_data.get("anomaly_count", 0)
    if anomaly_count > 0:
        recommendations.append(Recommendation(
            id="unusual_transactions",
            type="anomaly",
            title="Unusual Transactions Detected",
            description=f"We detected {anomaly_count} unusual transaction(s) that deviate from your normal spending patterns. Please review them for accuracy.",
            severity="critical",
            category="Security",
            potential_savings=0,
            action="Review anomalies now",
            created_at=datetime.now().isoformat()
        ))
    
    # Smart Savings Tips
    expenses = user_data.get("total_expenses", 0)
    if expenses > 0:
        # Subscription optimization
        recommendations.append(Recommendation(
            id="subscription_review",
            type="savings_tip",
            title="Review Subscriptions",
            description="It's been a while since you reviewed recurring subscriptions. Cancel unused services to save money each month.",
            severity="info",
            category="Entertainment",
            potential_savings=50,
            action="Audit subscriptions",
            created_at=datetime.now().isoformat()
        ))
        
        # Dining out insight
        dining_amount = next((c['amount'] for c in user_data.get('categories', []) if c['category'] == 'Dining'), 0)
        if dining_amount > 300:
            potential = dining_amount * 0.3
            recommendations.append(Recommendation(
                id="reduce_dining_out",
                type="savings_tip",
                title="Reduce Dining Out",
                description=f"You spent {dining_amount:.0f} TND on dining out. Cooking at home more often could save you {potential:.0f} TND per month.",
                severity="info",
                category="Dining",
                potential_savings=potential,
                action="Meal prep on weekends",
                created_at=datetime.now().isoformat()
            ))
    
    return recommendations


@router.get("/", response_model=RecommendationsResponse)
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    """
    Get personalized AI recommendations
    """
    # Mock user data (replace with real database queries)
    user_data = {
        "total_income": 4500,
        "total_expenses": 2850,
        "net_savings": 1650,
        "savings_rate": 36.7,
        "top_category": {
            "name": "Groceries",
            "amount": 850,
            "percentage": 29.8
        },
        "budgets": [
            {"category": "Groceries", "spent": 850, "budget": 800},
            {"category": "Transport", "spent": 450, "budget": 500},
            {"category": "Bills & Utilities", "spent": 620, "budget": 600},
        ],
        "categories": [
            {"category": "Groceries", "amount": 850, "percentage": 29.8},
            {"category": "Dining", "amount": 380, "percentage": 13.3},
        ],
        "at_risk_goals": ["New Laptop"],
        "anomaly_count": 2,
    }
    
    recommendations = generate_recommendations(user_data)
    total_savings = sum(r.potential_savings for r in recommendations)
    
    return RecommendationsResponse(
        recommendations=recommendations,
        total_potential_savings=total_savings
    )


@router.post("/dismiss/{recommendation_id}")
async def dismiss_recommendation(
    recommendation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Dismiss a recommendation
    """
    return {"message": "Recommendation dismissed", "id": recommendation_id}

@router.get("/random", response_model=Recommendation)
async def get_random_recommendation(current_user: dict = Depends(get_current_user)):
    """
    Get a random AI-powered financial insight
    """
    import random
    
    # Mock user data
    user_data = {
        "total_income": 4500,
        "total_expenses": 2850,
        "net_savings": 1650,
        "savings_rate": 36.7,
        "total_transactions": 124,
    }
    
    # Collection of random insights
    random_insights = [
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Coffee Shop Savings",
            description=f"If you reduce coffee shop visits by 50%, you could save approximately {150:.0f} TND per month. That's {150 * 12:.0f} TND per year!",
            severity="info",
            category="Dining",
            potential_savings=150,
            action="Make coffee at home 3 days a week",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Energy Efficiency",
            description="Switching to LED bulbs and unplugging devices could reduce your electricity bill by 15-20%. Small changes, big impact!",
            severity="info",
            category="Bills & Utilities",
            potential_savings=30,
            action="Audit home energy usage",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="spending_insight",
            title="Grocery Shopping Pattern",
            description=f"You've made {user_data['total_transactions']} transactions this month. Shopping with a list and buying in bulk could reduce impulse purchases by 25%.",
            severity="info",
            category="Groceries",
            potential_savings=75,
            action="Create weekly meal plans",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="goal_tip",
            title="Emergency Fund Rule",
            description="Financial experts recommend having 3-6 months of expenses saved. You're on track! Consider increasing your emergency fund target to 6 months.",
            severity="info",
            category="Savings",
            potential_savings=0,
            action="Review emergency fund goal",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="50/30/20 Budget Rule",
            description="Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings. Your current split could be optimized for better financial health.",
            severity="info",
            category="Budget",
            potential_savings=200,
            action="Analyze your spending split",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="spending_insight",
            title="Subscription Audit",
            description="The average person wastes 42 TND/month on unused subscriptions. When did you last use all your streaming services?",
            severity="warning",
            category="Entertainment",
            potential_savings=42,
            action="Cancel unused subscriptions",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Automated Savings",
            description=f"With your income of {user_data['total_income']:.0f} TND, setting up automatic transfers of just 10% would save {user_data['total_income'] * 0.1:.0f} TND monthly without effort.",
            severity="info",
            category="Savings",
            potential_savings=user_data['total_income'] * 0.1,
            action="Set up automatic transfers",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="spending_insight",
            title="Transportation Savings",
            description="Using public transport 2 days a week or carpooling could save you up to 80 TND monthly on fuel and parking.",
            severity="info",
            category="Transport",
            potential_savings=80,
            action="Plan carpool schedule",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="goal_tip",
            title="Investment Tip",
            description="You're saving well! Consider diversifying 20% of your savings into low-risk investments for better long-term returns.",
            severity="info",
            category="Investment",
            potential_savings=0,
            action="Consult financial advisor",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Meal Prep Strategy",
            description="Cooking dinner at home instead of ordering out 4 times a week could save you 250 TND monthly. That's a vacation fund!",
            severity="info",
            category="Dining",
            potential_savings=250,
            action="Start meal prepping Sundays",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="spending_insight",
            title="Weekend Spending Alert",
            description="Data shows you spend 40% more on weekends. Being mindful of weekend impulse purchases could save 120 TND/month.",
            severity="warning",
            category="Shopping",
            potential_savings=120,
            action="Set weekend spending limit",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Cash-Back Rewards",
            description="Are you maximizing credit card rewards? Using the right card for different categories could earn you 60-100 TND monthly.",
            severity="info",
            category="Finance",
            potential_savings=80,
            action="Review credit card benefits",
            created_at=datetime.now().isoformat()
        ),
    ]
    
    # Return a random recommendation
    return random.choice(random_insights)


@router.get("/test-random", response_model=Recommendation)
async def test_random_recommendation():
    """
    Test endpoint for random recommendations (no auth required)
    """
    import random
    
    random_insights = [
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Coffee Shop Savings",
            description="If you reduce coffee shop visits by 50%, you could save approximately 150 TND per month. That's 1,800 TND per year!",
            severity="info",
            category="Dining",
            potential_savings=150,
            action="Make coffee at home 3 days a week",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="savings_tip",
            title="Energy Efficiency Tip",
            description="Switching to LED bulbs and unplugging devices could reduce your electricity bill by 15-20%. Small changes, big impact!",
            severity="info",
            category="Bills & Utilities",
            potential_savings=30,
            action="Audit home energy usage",
            created_at=datetime.now().isoformat()
        ),
        Recommendation(
            id=f"random_{datetime.now().timestamp()}",
            type="spending_insight",
            title="Subscription Audit",
            description="The average person wastes 42 TND/month on unused subscriptions. When did you last use all your streaming services?",
            severity="warning",
            category="Entertainment",
            potential_savings=42,
            action="Cancel unused subscriptions",
            created_at=datetime.now().isoformat()
        ),
    ]
    
    return random.choice(random_insights)