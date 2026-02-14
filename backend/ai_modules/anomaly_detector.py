"""
Anomaly Detection Module
- Isolation Forest for transaction anomalies
- Multi-feature detection (amount, timing, category)
- Explainable anomaly scoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """Detect unusual financial transactions"""
    
    def __init__(self, contamination: float = 0.05):
        """
        Initialize detector
        
        Args:
            contamination: Expected proportion of outliers (0.05 = 5%)
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_stats = {}  # For generating explanations
    
    def extract_features(self, transactions: List[Dict]) -> pd.DataFrame:
        """
        Extract features for anomaly detection
        
        Features:
        - amount (normalized)
        - day_of_month
        - day_of_week
        - category_encoded
        - days_since_last_transaction
        - amount_deviation_from_category_avg
        """
        df = pd.DataFrame(transactions)
        
        # Convert dates
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df.sort_values('transaction_date')
        
        # Temporal features
        df['day_of_month'] = df['transaction_date'].dt.day
        df['day_of_week'] = df['transaction_date'].dt.dayofweek
        df['hour'] = df['transaction_date'].dt.hour if 'hour' in df.columns else 12
        
        # Category encoding (use factorize for unknown categories)
        df['category_encoded'], _ = pd.factorize(df['category'])
        
        # Amount features
        df['amount_log'] = np.log1p(df['amount'])  # Log transform for scale
        
        # Category-based features
        category_stats = df.groupby('category')['amount'].agg(['mean', 'std']).to_dict()
        df['category_avg'] = df['category'].map(category_stats['mean'])
        df['category_std'] = df['category'].map(category_stats['std']).fillna(1)
        df['amount_deviation'] = (df['amount'] - df['category_avg']) / df['category_std']
        
        # Temporal spacing
        df['days_since_last'] = df['transaction_date'].diff().dt.days.fillna(30)
        
        # Store stats for explanations
        self.feature_stats = {
            'amount_mean': df['amount'].mean(),
            'amount_std': df['amount'].std(),
            'category_avg': category_stats['mean'],
            'category_std': category_stats.get('std', {})
        }
        
        # Select features for model
        feature_cols = [
            'amount_log',
            'day_of_month',
            'day_of_week',
            'category_encoded',
            'amount_deviation',
            'days_since_last'
        ]
        
        return df[feature_cols + ['amount', 'category', 'transaction_date']].copy()
    
    def train(self, transactions: List[Dict]) -> Dict:
        """
        Train anomaly detection model
        
        Returns:
            Training metrics
        """
        if len(transactions) < 20:
            raise ValueError("Need at least 20 transactions for training")
        
        # Extract features
        df = self.extract_features(transactions)
        feature_cols = [
            'amount_log', 'day_of_month', 'day_of_week',
            'category_encoded', 'amount_deviation', 'days_since_last'
        ]
        X = df[feature_cols].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Get anomaly scores
        scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        n_anomalies = (predictions == -1).sum()
        
        return {
            'n_transactions': len(transactions),
            'n_anomalies_detected': int(n_anomalies),
            'anomaly_rate': float(n_anomalies / len(transactions)),
            'score_mean': float(scores.mean()),
            'score_std': float(scores.std())
        }
    
    def detect(
        self,
        transaction: Dict,
        historical_transactions: List[Dict]
    ) -> Dict:
        """
        Detect if a transaction is anomalous
        
        Args:
            transaction: Single transaction to check
            historical_transactions: User's transaction history
            
        Returns:
            {
                'is_anomaly': bool,
                'anomaly_score': float,
                'anomaly_type': str,
                'explanation': str,
                'baseline_comparison': dict
            }
        """
        if not self.is_trained:
            # Train on historical data if not trained
            if len(historical_transactions) >= 20:
                self.train(historical_transactions)
            else:
                return {
                    'is_anomaly': False,
                    'anomaly_score': 0.0,
                    'anomaly_type': 'insufficient_data',
                    'explanation': "Not enough historical data for anomaly detection",
                    'baseline_comparison': {}
                }
        
        # Prepare data with historical context
        all_transactions = historical_transactions + [transaction]
        df = self.extract_features(all_transactions)
        
        # Get features for the new transaction (last row)
        feature_cols = [
            'amount_log', 'day_of_month', 'day_of_week',
            'category_encoded', 'amount_deviation', 'days_since_last'
        ]
        X_new = df[feature_cols].iloc[-1:].values
        X_new_scaled = self.scaler.transform(X_new)
        
        # Predict
        score = self.model.score_samples(X_new_scaled)[0]
        is_anomaly = self.model.predict(X_new_scaled)[0] == -1
        
        # Determine anomaly type and generate explanation
        txn_data = df.iloc[-1]
        category = transaction['category']
        amount = transaction['amount']
        
        # Calculate baselines
        category_avg = self.feature_stats['category_avg'].get(category, amount)
        amount_mean = self.feature_stats['amount_mean']
        
        baseline_comparison = {
            'transaction_amount': float(amount),
            'category_average': float(category_avg),
            'overall_average': float(amount_mean),
            'deviation_from_category': float(amount / category_avg) if category_avg > 0 else 1.0,
            'deviation_from_overall': float(amount / amount_mean) if amount_mean > 0 else 1.0
        }
        
        # Determine anomaly type
        anomaly_type = 'normal'
        explanation = "Transaction appears normal"
        
        if is_anomaly:
            if amount > category_avg * 2:
                anomaly_type = 'amount_spike'
                explanation = (
                    f"Amount ({amount:.2f} TND) is {amount/category_avg:.1f}x "
                    f"your average {category} spend ({category_avg:.2f} TND)"
                )
            elif amount > amount_mean * 3:
                anomaly_type = 'unusual_amount'
                explanation = (
                    f"Amount ({amount:.2f} TND) is significantly higher than "
                    f"your typical transaction ({amount_mean:.2f} TND)"
                )
            elif txn_data['days_since_last'] < 1:
                anomaly_type = 'frequency_anomaly'
                explanation = "Multiple transactions in a short time period"
            else:
                anomaly_type = 'pattern_anomaly'
                explanation = "Transaction pattern differs from your usual behavior"
        
        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(score),
            'anomaly_type': anomaly_type,
            'explanation': explanation,
            'baseline_comparison': baseline_comparison,
            'confidence': float(abs(score))  # Higher absolute score = more confident
        }
    
    def batch_detect(
        self,
        transactions: List[Dict]
    ) -> List[Dict]:
        """
        Detect anomalies in a batch of transactions
        
        Returns:
            List of anomaly detection results (only anomalies)
        """
        if not self.is_trained or len(transactions) < 20:
            self.train(transactions)
        
        df = self.extract_features(transactions)
        feature_cols = [
            'amount_log', 'day_of_month', 'day_of_week',
            'category_encoded', 'amount_deviation', 'days_since_last'
        ]
        X = df[feature_cols].values
        X_scaled = self.scaler.transform(X)
        
        scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        anomalies = []
        for idx, (score, pred) in enumerate(zip(scores, predictions)):
            if pred == -1:
                txn = transactions[idx]
                anomalies.append({
                    'transaction_id': txn.get('id'),
                    'transaction_date': str(txn['transaction_date']),
                    'amount': txn['amount'],
                    'category': txn['category'],
                    'description': txn.get('description', ''),
                    'anomaly_score': float(score),
                    'explanation': self._generate_explanation(txn, df.iloc[idx])
                })
        
        return sorted(anomalies, key=lambda x: x['anomaly_score'])[:10]  # Top 10
    def detect_single(
        self,
        transaction: Dict,
        historical_transactions: List[Dict]
    ) -> Dict:
        """
        Detect if a single transaction is anomalous based on historical data
        
        Args:
            transaction: Single transaction to check
            historical_transactions: Historical transactions (for training/context)
            
        Returns:
            Anomaly result dict
        """
        if len(historical_transactions) < 20:
            raise ValueError("Need at least 20 historical transactions")
        
        # Train on historical data ONLY
        self.train(historical_transactions)
        
        # Prepare features for the single transaction
        features = self._prepare_features([transaction])
        
        if features.empty:
            return {
                'id': transaction.get('id'),
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'explanation': 'Insufficient data for detection'
            }
        
        # Predict anomaly score
        X_scaled = self.scaler.transform(features[self.feature_columns])
        anomaly_score = self.model.score_samples(X_scaled)[0]
        
        # Convert score to 0-1 range (more negative = more anomalous)
        # Typical scores range from -1 to 0
        normalized_score = max(0, min(1, abs(anomaly_score)))
        
        # Check if anomalous (threshold based on contamination)
        is_anomaly = anomaly_score < self.threshold
        
        # Generate explanation
        explanation = self._generate_explanation(
            transaction, 
            historical_transactions,
            normalized_score
        )
        
        return {
            'id': transaction.get('id'),
            'is_anomaly': is_anomaly,
            'anomaly_score': normalized_score,
            'explanation': explanation
        }


    def _generate_explanation(
        self,
        transaction: Dict,
        historical: List[Dict],
        score: float
    ) -> str:
        """Generate human-readable explanation for anomaly"""
        amount = transaction.get('amount', 0)
        category = transaction.get('category', 'Unknown')
        
        # Calculate stats from historical data
        category_txns = [t for t in historical if t.get('category') == category]
        
        if not category_txns:
            return f"No historical {category} transactions to compare"
        
        avg_amount = sum(t.get('amount', 0) for t in category_txns) / len(category_txns)
        max_amount = max(t.get('amount', 0) for t in category_txns)
        
        if amount > avg_amount * 3:
            multiplier = amount / avg_amount
            return f"Amount is {multiplier:.1f}x your average {category} spend"
        elif amount > max_amount:
            return f"This exceeds your highest {category} transaction ({max_amount:.2f})"
        elif amount < avg_amount * 0.2:
            return f"Unusually low amount for {category}"
        else:
            return f"Unusual transaction pattern detected for {category}"

    
    def save_model(self, path: str):
        """Save trained model"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_stats': self.feature_stats,
            'contamination': self.contamination
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str):
        """Load pre-trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_stats = model_data['feature_stats']
        self.contamination = model_data['contamination']
        self.is_trained = True


# Example usage
if __name__ == "__main__":
    from datetime import date, timedelta
    
    # Demo data with anomaly
    demo_transactions = []
    base_date = date(2026, 1, 1)
    
    # Normal transactions
    for i in range(30):
        demo_transactions.append({
            'id': i,
            'transaction_date': base_date + timedelta(days=i),
            'amount': np.random.normal(200, 50),  # Normal ~200 TND
            'category': 'Groceries',
            'description': f'Transaction {i}'
        })
    
    # Add anomaly
    demo_transactions.append({
        'id': 30,
        'transaction_date': base_date + timedelta(days=30),
        'amount': 1500,  # Anomalous amount
        'category': 'Groceries',
        'description': 'Large purchase'
    })
    
    detector = AnomalyDetector(contamination=0.1)
    metrics = detector.train(demo_transactions[:-1])
    print(f"Trained on {metrics['n_transactions']} transactions")
    
    # Detect anomaly
    result = detector.detect(demo_transactions[-1], demo_transactions[:-1])
    print(f"\nAnomaly detected: {result['is_anomaly']}")
    print(f"Score: {result['anomaly_score']:.3f}")
    print(f"Explanation: {result['explanation']}")
