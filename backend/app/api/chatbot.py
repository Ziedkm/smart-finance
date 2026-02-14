"""
Chatbot API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from app.dependencies import get_current_user

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatMessage(BaseModel):
    message: str
    

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    data: Dict[str, Any] = {}


class ChatbotService:
    """Simple rule-based chatbot for finance queries"""
    
    def __init__(self):
        self.intents = {
            "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
            "spending": ["spent", "spending", "expenses", "money", "spend"],
            "budget": ["budget", "budgets", "limit"],
            "savings": ["save", "saved", "savings", "saving"],
            "goals": ["goal", "goals", "target"],
            "categories": ["category", "categories", "where", "what"],
            "anomaly": ["unusual", "anomaly", "weird", "strange", "suspicious"],
            "help": ["help", "what can you do", "how", "commands"],
        }
        
    def detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        for intent, keywords in self.intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "unknown"
    
    def generate_response(
        self, 
        message: str, 
        user_data: Dict[str, Any]
    ) -> ChatResponse:
        """Generate response based on intent and user data"""
        intent = self.detect_intent(message)
        
        if intent == "greeting":
            return ChatResponse(
                response="Hello! 👋 I'm your Smart Finance assistant. I can help you understand your spending, budgets, savings, and financial goals. What would you like to know?",
                suggestions=[
                    "Where did my money go?",
                    "Am I on track with my budget?",
                    "How much have I saved?",
                    "Show my spending by category"
                ]
            )
        
        elif intent == "spending":
            total_expenses = user_data.get("total_expenses", 0)
            top_category = user_data.get("top_category", {})
            
            return ChatResponse(
                response=f"💸 You've spent **{total_expenses:.0f} TND** this month. Your biggest expense category is **{top_category.get('name', 'N/A')}** with {top_category.get('amount', 0):.0f} TND ({top_category.get('percentage', 0):.1f}%).",
                suggestions=[
                    "Show spending by category",
                    "Compare to last month",
                    "Show unusual transactions"
                ],
                data={
                    "total_expenses": total_expenses,
                    "top_category": top_category
                }
            )
        
        elif intent == "budget":
            budget_adherence = user_data.get("budget_adherence", 0)
            over_budget = user_data.get("over_budget_categories", [])
            
            status = "excellent" if budget_adherence >= 90 else "good" if budget_adherence >= 70 else "needs attention"
            
            response_text = f"📊 Your budget adherence is **{budget_adherence:.1f}%** - that's {status}!"
            
            if over_budget:
                response_text += f"\n\n⚠️ You're over budget in: {', '.join(over_budget)}"
            
            return ChatResponse(
                response=response_text,
                suggestions=[
                    "Show budget details",
                    "How to improve?",
                    "Set new budget"
                ],
                data={
                    "budget_adherence": budget_adherence,
                    "over_budget": over_budget
                }
            )
        
        elif intent == "savings":
            net_savings = user_data.get("net_savings", 0)
            savings_rate = user_data.get("savings_rate", 0)
            
            return ChatResponse(
                response=f"💰 You've saved **{net_savings:.0f} TND** this month! That's a **{savings_rate:.1f}%** savings rate. Great job! 🎉",
                suggestions=[
                    "How can I save more?",
                    "Show my goals",
                    "Compare savings over time"
                ],
                data={
                    "net_savings": net_savings,
                    "savings_rate": savings_rate
                }
            )
        
        elif intent == "goals":
            active_goals = user_data.get("active_goals", 0)
            on_track = user_data.get("goals_on_track", 0)
            
            return ChatResponse(
                response=f"🎯 You have **{active_goals}** active goals. {on_track} are on track to be completed on time!",
                suggestions=[
                    "Show goal details",
                    "Create new goal",
                    "How to reach goals faster?"
                ],
                data={
                    "active_goals": active_goals,
                    "on_track": on_track
                }
            )
        
        elif intent == "categories":
            categories = user_data.get("categories", [])
            
            response_text = "📋 Here's your spending breakdown:\n\n"
            for cat in categories[:5]:
                response_text += f"• **{cat['category']}**: {cat['amount']:.0f} TND ({cat['percentage']:.1f}%)\n"
            
            return ChatResponse(
                response=response_text,
                suggestions=[
                    "Show all categories",
                    "Which category to reduce?",
                    "Set category budget"
                ],
                data={"categories": categories}
            )
        
        elif intent == "anomaly":
            anomaly_count = user_data.get("anomaly_count", 0)
            
            if anomaly_count > 0:
                return ChatResponse(
                    response=f"🚨 I detected **{anomaly_count}** unusual transaction(s) this month. These might need your attention!",
                    suggestions=[
                        "Show anomalies",
                        "Why are they unusual?",
                        "Mark as normal"
                    ],
                    data={"anomaly_count": anomaly_count}
                )
            else:
                return ChatResponse(
                    response="✅ No unusual transactions detected! All your spending looks normal.",
                    suggestions=["Show recent transactions", "View spending patterns"]
                )
        
        elif intent == "help":
            return ChatResponse(
                response="""I can help you with:

• 💸 **Spending**: "Where did my money go?"
• 📊 **Budgets**: "Am I on track with my budget?"
• 💰 **Savings**: "How much have I saved?"
• 🎯 **Goals**: "Show my financial goals"
• 📋 **Categories**: "Show spending by category"
• 🚨 **Anomalies**: "Any unusual transactions?"

Just ask me anything about your finances!""",
                suggestions=[
                    "Where did my money go?",
                    "Show my budget status",
                    "How much have I saved?"
                ]
            )
        
        else:
            return ChatResponse(
                response="I'm not sure I understand. Could you rephrase that? I can help with spending, budgets, savings, goals, and more!",
                suggestions=[
                    "Where did my money go?",
                    "Show budget status",
                    "Help"
                ]
            )


# Instantiate service
chatbot_service = ChatbotService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat endpoint - accepts user message and returns AI response
    """
    # Mock user data (in production, fetch from database)
    user_data = {
        "total_expenses": 2850,
        "total_income": 4500,
        "net_savings": 1650,
        "savings_rate": 36.7,
        "budget_adherence": 89.5,
        "top_category": {
            "name": "Groceries",
            "amount": 850,
            "percentage": 29.8
        },
        "over_budget_categories": ["Groceries", "Bills & Utilities"],
        "categories": [
            {"category": "Groceries", "amount": 850, "percentage": 29.8},
            {"category": "Transport", "amount": 450, "percentage": 15.8},
            {"category": "Dining", "amount": 380, "percentage": 13.3},
            {"category": "Bills & Utilities", "amount": 620, "percentage": 21.8},
            {"category": "Entertainment", "amount": 300, "percentage": 10.5},
        ],
        "active_goals": 3,
        "goals_on_track": 2,
        "anomaly_count": 2,
    }
    
    response = chatbot_service.generate_response(message.message, user_data)
    return response


@router.post("/test-chat", response_model=ChatResponse)
async def test_chat(message: ChatMessage):
    """
    Test chat endpoint (no auth required)
    """
    user_data = {
        "total_expenses": 2850,
        "total_income": 4500,
        "net_savings": 1650,
        "savings_rate": 36.7,
        "budget_adherence": 89.5,
        "top_category": {
            "name": "Groceries",
            "amount": 850,
            "percentage": 29.8
        },
        "over_budget_categories": ["Groceries", "Bills & Utilities"],
        "categories": [
            {"category": "Groceries", "amount": 850, "percentage": 29.8},
            {"category": "Transport", "amount": 450, "percentage": 15.8},
            {"category": "Dining", "amount": 380, "percentage": 13.3},
        ],
        "active_goals": 3,
        "goals_on_track": 2,
        "anomaly_count": 2,
    }
    
    response = chatbot_service.generate_response(message.message, user_data)
    return response
