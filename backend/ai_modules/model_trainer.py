"""
Model Training Orchestrator
- Coordinates training of all AI modules
- Generates synthetic training data if needed
- Validates models and saves artifacts
"""

import os
import pickle
from typing import Dict
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from .expense_classifier import ExpenseClassifier
from .anomaly_detector import AnomalyDetector


class ModelTrainer:
    """Orchestrate training of all AI modules"""
    
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
    
    def generate_synthetic_training_data(self, n_samples: int = 200) -> pd.DataFrame:
        """
        Generate synthetic transaction data for initial model training
        
        Returns:
            DataFrame with synthetic transactions
        """
        categories = [
            'Groceries', 'Transport', 'Dining', 'Bills & Utilities',
            'Healthcare', 'Shopping', 'Entertainment', 'Education', 'Income'
        ]
        
        merchants = {
            'Groceries': ['Carrefour', 'Monoprix', 'Supermarket', 'Market Fresh'],
            'Transport': ['Shell', 'Total', 'Agil', 'Uber', 'Taxi'],
            'Dining': ['Restaurant', 'Cafe', 'Pizza Place', 'Sushi Bar'],
            'Bills & Utilities': ['STEG', 'Topnet', 'Ooredoo', 'Orange'],
            'Healthcare': ['Pharmacy', 'Hospital', 'Clinic', 'Doctor'],
            'Shopping': ['FNAC', 'Mall', 'Store', 'Online Shop'],
            'Entertainment': ['Cinema', 'Netflix', 'Spotify', 'Gym'],
            'Education': ['University', 'Bookstore', 'Course', 'Training'],
            'Income': ['Employer', 'Salary', 'Freelance', 'Payment']
        }
        
        descriptions = {
            'Groceries': ['Weekly shopping', 'Groceries', 'Food', 'Market visit'],
            'Transport': ['Gas refill', 'Fuel', 'Taxi ride', 'Transport'],
            'Dining': ['Dinner', 'Lunch', 'Coffee', 'Restaurant meal'],
            'Bills & Utilities': ['Internet bill', 'Phone bill', 'Electricity', 'Utilities'],
            'Healthcare': ['Medicine', 'Doctor visit', 'Prescription', 'Medical'],
            'Shopping': ['New clothes', 'Electronics', 'Purchase', 'Shopping'],
            'Entertainment': ['Movie tickets', 'Subscription', 'Gym membership', 'Entertainment'],
            'Education': ['Textbook', 'Course fee', 'Training', 'Education'],
            'Income': ['Monthly salary', 'Payment received', 'Income', 'Salary']
        }
        
        transactions = []
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(n_samples):
            category = np.random.choice(categories, p=[0.15, 0.12, 0.12, 0.10, 0.05, 0.12, 0.08, 0.06, 0.20])
            merchant = np.random.choice(merchants[category])
            description = np.random.choice(descriptions[category])
            
            # Category-specific amount ranges
            if category == 'Income':
                amount = np.random.normal(3000, 500)
                txn_type = 'income'
            elif category == 'Groceries':
                amount = np.random.normal(150, 50)
                txn_type = 'expense'
            elif category == 'Transport':
                amount = np.random.normal(100, 30)
                txn_type = 'expense'
            elif category == 'Bills & Utilities':
                amount = np.random.normal(120, 20)
                txn_type = 'expense'
            else:
                amount = np.random.normal(200, 80)
                txn_type = 'expense'
            
            amount = max(10, amount)  # Minimum 10 TND
            
            transaction_date = base_date + timedelta(days=np.random.randint(0, 180))
            
            transactions.append({
                'id': i,
                'transaction_date': transaction_date,
                'description': description,
                'merchant': merchant,
                'amount': round(amount, 2),
                'category': category,
                'transaction_type': txn_type
            })
        
        return pd.DataFrame(transactions)
    
    def train_all_models(self, transactions_df: pd.DataFrame = None) -> Dict:
        """
        Train all AI models
        
        Args:
            transactions_df: Optional transaction data. If None, generates synthetic data.
            
        Returns:
            Training metrics for all models
        """
        print("🚀 Starting AI model training pipeline...\n")
        
        # Generate synthetic data if needed
        if transactions_df is None:
            print("📊 Generating synthetic training data...")
            transactions_df = self.generate_synthetic_training_data(n_samples=300)
            print(f"   Generated {len(transactions_df)} synthetic transactions\n")
        
        training_results = {}
        
        # 1. Train Expense Classifier
        print("🏷️  Training Expense Classifier...")
        classifier = ExpenseClassifier()
        
        training_data = transactions_df[transactions_df['transaction_type'] == 'expense'].to_dict('records')
        classifier_metrics = classifier.train(training_data, [])
        
        classifier_path = os.path.join(self.models_dir, 'expense_classifier.pkl')
        classifier.save_model(classifier_path)
        
        print(f"   ✅ Accuracy: {classifier_metrics['accuracy']:.2%}")
        print(f"   ✅ Trained on {classifier_metrics['n_train']} samples")
        print(f"   ✅ Saved to {classifier_path}\n")
        
        training_results['expense_classifier'] = classifier_metrics
        
        # 2. Train Anomaly Detector
        print("🔍 Training Anomaly Detector...")
        detector = AnomalyDetector(contamination=0.05)
        
        anomaly_data = transactions_df.to_dict('records')
        detector_metrics = detector.train(anomaly_data)
        
        detector_path = os.path.join(self.models_dir, 'anomaly_detector.pkl')
        detector.save_model(detector_path)
        
        print(f"   ✅ Detected {detector_metrics['n_anomalies_detected']} anomalies in training data")
        print(f"   ✅ Anomaly rate: {detector_metrics['anomaly_rate']:.2%}")
        print(f"   ✅ Saved to {detector_path}\n")
        
        training_results['anomaly_detector'] = detector_metrics
        
        # 3. Test forecaster (no training needed for linear regression)
        print("📈 Forecaster: Using linear regression (no pre-training needed)")
        print("   ✅ Will train on-demand with user data\n")
        
        training_results['forecaster'] = {'status': 'ready', 'method': 'linear_regression'}
        
        # 4. Test recommendation engine (rule-based, no training)
        print("💡 Recommendation Engine: Rule-based system (no training needed)")
        print("   ✅ Ready to generate recommendations\n")
        
        training_results['recommendation_engine'] = {'status': 'ready', 'method': 'rule_based'}
        
        # 5. Test chatbot (template-based, no training)
        print("💬 Chatbot: Template-based responses (no training needed)")
        print("   ✅ Ready for conversations\n")
        
        training_results['chatbot'] = {'status': 'ready', 'method': 'template_based'}
        
        print("✨ All AI modules trained successfully!\n")
        
        return training_results


# Main training script
if __name__ == "__main__":
    trainer = ModelTrainer(models_dir='../models')
    
    print("=" * 60)
    print("SMART FINANCE - AI MODEL TRAINING")
    print("=" * 60)
    print()
    
    results = trainer.train_all_models()
    
    print("=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print()
    
    for module, metrics in results.items():
        print(f"📦 {module}:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        print()
