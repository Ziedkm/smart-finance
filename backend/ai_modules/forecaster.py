"""
Financial Forecasting Module
- Linear regression baseline (fast, explainable)
- Prophet integration option (commented out for MVP)
- Monthly expense prediction by category
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


class FinancialForecaster:
    """Predict future expenses using historical data"""
    
    def __init__(self, method: str = 'linear'):
        """
        Initialize forecaster
        
        Args:
            method: 'linear' (MVP) or 'prophet' (post-MVP)
        """
        self.method = method
        self.models = {}  # category -> model mapping
        self.last_training_date = None
    
    def prepare_time_series(
        self, 
        transactions: List[Dict],
        category: str = 'all'
    ) -> pd.DataFrame:
        """
        Convert transaction list to time series
        
        Returns:
            DataFrame with columns: [date, amount, month_index]
        """
        df = pd.DataFrame(transactions)
        
        if category != 'all':
            df = df[df['category'] == category]
        
        # Group by month
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['month'] = df['transaction_date'].dt.to_period('M')
        
        monthly = df.groupby('month').agg({
            'amount': 'sum'
        }).reset_index()
        
        monthly['month'] = monthly['month'].dt.to_timestamp()
        monthly['month_index'] = range(len(monthly))
        
        return monthly
    
    def train_linear_model(
        self,
        monthly_data: pd.DataFrame
    ) -> Tuple[LinearRegression, Dict]:
        """
        Train linear regression model
        
        Returns:
            (model, metrics)
        """
        if len(monthly_data) < 3:
            raise ValueError("Need at least 3 months of data")
        
        X = monthly_data[['month_index']].values
        y = monthly_data['amount'].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate metrics
        y_pred = model.predict(X)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mape = np.mean(np.abs((y - y_pred) / (y + 1e-10))) * 100  # Avoid division by zero
        
        return model, {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r_squared': model.score(X, y),
            'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing',
            'monthly_change': float(model.coef_[0])
        }
    
    def forecast(
        self,
        transactions: List[Dict],
        category: str = 'all',
        horizon_months: int = 1
    ) -> Dict:
        """
        Forecast future expenses
        
        Args:
            transactions: Historical transaction data
            category: Category to forecast ('all' for total)
            horizon_months: Number of months to forecast (1-6)
            
        Returns:
            {
                'predictions': [(date, amount, lower_bound, upper_bound), ...],
                'confidence': float,
                'explanation': str,
                'trend': str,
                'metrics': dict
            }
        """
        # Prepare data
        monthly_data = self.prepare_time_series(transactions, category)
        
        if len(monthly_data) < 3:
            return {
                'predictions': [],
                'confidence': 0.0,
                'explanation': "Insufficient historical data (need 3+ months)",
                'trend': 'unknown',
                'metrics': {}
            }
        
        # Train model
        model, metrics = self.train_linear_model(monthly_data)
        
        # Generate predictions
        last_month_index = monthly_data['month_index'].max()
        last_date = monthly_data['month'].max()
        
        predictions = []
        for i in range(1, horizon_months + 1):
            future_month_index = last_month_index + i
            predicted_amount = model.predict([[future_month_index]])[0]
            
            # Calculate uncertainty (using historical RMSE)
            uncertainty = metrics['rmse'] * 1.96  # 95% confidence interval
            lower_bound = max(0, predicted_amount - uncertainty)
            upper_bound = predicted_amount + uncertainty
            
            future_date = last_date + pd.DateOffset(months=i)
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'amount': float(predicted_amount),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            })
        
        # Generate explanation
        if metrics['trend'] == 'increasing':
            trend_text = f"increasing by approximately {abs(metrics['monthly_change']):.2f} TND per month"
        else:
            trend_text = f"decreasing by approximately {abs(metrics['monthly_change']):.2f} TND per month"
        
        explanation = (
            f"Based on {len(monthly_data)} months of historical data, "
            f"your {category} expenses are {trend_text}. "
            f"Forecast accuracy (MAPE): {metrics['mape']:.1f}%"
        )
        
        # Confidence based on MAPE (lower is better)
        if metrics['mape'] < 15:
            confidence = 0.9
        elif metrics['mape'] < 25:
            confidence = 0.7
        elif metrics['mape'] < 40:
            confidence = 0.5
        else:
            confidence = 0.3
        
        return {
            'predictions': predictions,
            'confidence': confidence,
            'explanation': explanation,
            'trend': metrics['trend'],
            'metrics': metrics
        }
    
    def forecast_by_category(
        self,
        transactions: List[Dict],
        top_n: int = 5
    ) -> Dict[str, Dict]:
        """
        Forecast top N spending categories
        
        Returns:
            {category_name: forecast_result, ...}
        """
        # Get top categories by total spend
        df = pd.DataFrame(transactions)
        top_categories = (
            df[df['transaction_type'] == 'expense']
            .groupby('category')['amount']
            .sum()
            .nlargest(top_n)
            .index
            .tolist()
        )
        
        forecasts = {}
        for category in top_categories:
            try:
                forecast = self.forecast(transactions, category, horizon_months=1)
                forecasts[category] = forecast
            except Exception as e:
                forecasts[category] = {
                    'predictions': [],
                    'confidence': 0.0,
                    'explanation': f"Forecast error: {str(e)}",
                    'trend': 'unknown',
                    'metrics': {}
                }
        
        return forecasts


# Example usage
if __name__ == "__main__":
    # Demo data
    from datetime import date
    
    demo_transactions = [
        {'transaction_date': date(2025, 10, 15), 'amount': 450, 'category': 'Groceries', 'transaction_type': 'expense'},
        {'transaction_date': date(2025, 11, 15), 'amount': 500, 'category': 'Groceries', 'transaction_type': 'expense'},
        {'transaction_date': date(2025, 12, 15), 'amount': 550, 'category': 'Groceries', 'transaction_type': 'expense'},
        {'transaction_date': date(2026, 1, 15), 'amount': 600, 'category': 'Groceries', 'transaction_type': 'expense'},
    ]
    
    forecaster = FinancialForecaster()
    result = forecaster.forecast(demo_transactions, category='Groceries', horizon_months=2)
    
    print("Forecast Results:")
    print(f"Trend: {result['trend']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Explanation: {result['explanation']}")
    print("\nPredictions:")
    for pred in result['predictions']:
        print(f"  {pred['date']}: {pred['amount']:.2f} TND (±{pred['upper_bound'] - pred['amount']:.2f})")
