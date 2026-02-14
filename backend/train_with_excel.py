"""
Train models with Excel/XLSX Kaggle data
"""

import pandas as pd
import os
from ai_modules.model_trainer import ModelTrainer
from ai_modules.expense_classifier import ExpenseClassifier
from ai_modules.anomaly_detector import AnomalyDetector


def load_excel_data(filepath: str) -> pd.DataFrame:
    """
    Load and standardize Excel dataset to our format
    
    Args:
        filepath: Path to XLSX file
    
    Returns:
        DataFrame with standardized columns
    """
    print(f"📂 Loading data from: {filepath}")
    
    # Read Excel file
    df = pd.read_excel(filepath)
    
    print(f"   Raw data: {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {df.columns.tolist()}\n")
    
    # Standardize column names (handle case variations)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    
    print(f"🔍 Standardized columns: {df.columns.tolist()}\n")
    
    # Map to our schema
    df_standard = pd.DataFrame({
        'id': range(len(df)),
        'transaction_date': pd.to_datetime(df['date']),
        'description': df['description'].astype(str),
        'merchant': df['description'].astype(str),  # Use description as merchant
        'amount': df['amount'].abs(),  # Ensure positive
        'category': df['category'].astype(str),
        'transaction_type': df['transaction_type'].str.lower().map({
            'debit': 'expense',
            'credit': 'income'
        }).fillna('expense'),
        'account_name': df.get('account_name', 'Main Account')  # Optional column
    })
    
    # Clean data
    df_standard = df_standard.dropna(subset=['amount', 'category', 'transaction_date'])
    df_standard = df_standard[df_standard['amount'] > 0]
    
    # Standardize categories to match our 10 categories
    category_mapping = {
        # Food & Dining
        'dining out': 'Dining',
        'dining': 'Dining',
        'restaurants': 'Dining',
        'food & dining': 'Dining',
        'groceries': 'Groceries',
        'grocery': 'Groceries',
        'food': 'Groceries',
        'supermarket': 'Groceries',
        
        # Transport
        'transportation': 'Transport',
        'transport': 'Transport',
        'gas': 'Transport',
        'fuel': 'Transport',
        'auto & transport': 'Transport',
        'car': 'Transport',
        'parking': 'Transport',
        'public transport': 'Transport',
        
        # Shopping
        'shopping': 'Shopping',
        'retail': 'Shopping',
        'clothing': 'Shopping',
        'electronics': 'Shopping',
        'online shopping': 'Shopping',
        
        # Bills & Utilities
        'bills': 'Bills & Utilities',
        'utilities': 'Bills & Utilities',
        'bills & utilities': 'Bills & Utilities',
        'phone': 'Bills & Utilities',
        'internet': 'Bills & Utilities',
        'electricity': 'Bills & Utilities',
        'water': 'Bills & Utilities',
        'rent': 'Bills & Utilities',
        'mortgage': 'Bills & Utilities',
        'insurance': 'Bills & Utilities',
        
        # Entertainment
        'entertainment': 'Entertainment',
        'recreation': 'Entertainment',
        'movies': 'Entertainment',
        'streaming': 'Entertainment',
        'subscriptions': 'Entertainment',
        'hobbies': 'Entertainment',
        'sports': 'Entertainment',
        
        # Healthcare
        'health': 'Healthcare',
        'healthcare': 'Healthcare',
        'health & fitness': 'Healthcare',
        'medical': 'Healthcare',
        'pharmacy': 'Healthcare',
        'doctor': 'Healthcare',
        'hospital': 'Healthcare',
        
        # Income
        'income': 'Income',
        'salary': 'Income',
        'paycheck': 'Income',
        'wages': 'Income',
        'freelance': 'Income',
        'business income': 'Income',
        'investment income': 'Income',
        
        # Education
        'education': 'Education',
        'books': 'Education',
        'tuition': 'Education',
        'courses': 'Education',
        'training': 'Education',
        
        # Personal Care
        'personal care': 'Shopping',
        'beauty': 'Shopping',
        'haircut': 'Shopping',
        
        # Travel
        'travel': 'Entertainment',
        'vacation': 'Entertainment',
        'hotel': 'Entertainment',
        'flights': 'Transport',
        
        # Misc
        'miscellaneous': 'Other',
        'misc': 'Other',
        'other': 'Other',
        'general': 'Other',
    }
    
    # Apply mapping (case-insensitive)
    df_standard['category'] = df_standard['category'].str.lower().str.strip()
    df_standard['category'] = df_standard['category'].replace(category_mapping)
    
    # Map any remaining unmapped categories to 'Other'
    valid_categories = [
        'Groceries', 'Transport', 'Dining', 'Bills & Utilities', 
        'Healthcare', 'Shopping', 'Entertainment', 'Education', 
        'Income', 'Other'
    ]
    df_standard.loc[~df_standard['category'].isin(valid_categories), 'category'] = 'Other'

    # Merge rare categories (with <5 samples) into 'Other' for better training
    category_counts = df_standard['category'].value_counts()
    rare_categories = category_counts[category_counts < 5].index.tolist()

    if rare_categories:
        print(f"   ⚠️  Merging rare categories into 'Other': {rare_categories}")
        df_standard.loc[df_standard['category'].isin(rare_categories), 'category'] = 'Other'
        
        print(f"   Updated category distribution:")
        for cat, count in df_standard['category'].value_counts().items():
            print(f"      - {cat}: {count} transactions ({count/len(df_standard)*100:.1f}%)")

    
    print("✅ Data standardized:")
    print(f"   Final rows: {len(df_standard)}")
    print(f"   Date range: {df_standard['transaction_date'].min().date()} to {df_standard['transaction_date'].max().date()}")
    print(f"   Categories: {sorted(df_standard['category'].unique())}")
    print(f"   Category distribution:")
    for cat, count in df_standard['category'].value_counts().items():
        print(f"      - {cat}: {count} transactions ({count/len(df_standard)*100:.1f}%)")
    print(f"   Transaction types: {df_standard['transaction_type'].value_counts().to_dict()}")
    print(f"   Total amount: {df_standard['amount'].sum():,.2f}")
    print(f"   Avg transaction: {df_standard['amount'].mean():.2f}")
    print(f"   Amount range: {df_standard['amount'].min():.2f} to {df_standard['amount'].max():.2f}")
    print()
    
    return df_standard


def train_on_excel_data(excel_path: str, sample_size: int = None):
    """
    Complete training pipeline with Excel data
    
    Args:
        excel_path: Path to XLSX file
        sample_size: Limit to N transactions (None = use all)
    """
    print("=" * 70)
    print("SMART FINANCE - TRAINING WITH EXCEL DATASET")
    print("=" * 70)
    print()
    
    # Load data
    df = load_excel_data(excel_path)
    
    if df is None or len(df) == 0:
        print("❌ Failed to load data or dataset is empty. Exiting.")
        return
    
    # Sample if requested
    if sample_size and len(df) > sample_size:
        print(f"📊 Sampling {sample_size} transactions from {len(df)} total...")
        df = df.sample(n=sample_size, random_state=42)
        print()
    
    # Train models
    print("🚀 Starting model training...\n")
    trainer = ModelTrainer(models_dir='../models')
    results = trainer.train_all_models(transactions_df=df)
    
    # Print summary
    print("=" * 70)
    print("TRAINING SUMMARY WITH REAL DATA")
    print("=" * 70)
    print()
    
    for module, metrics in results.items():
        print(f"📦 {module}:")
        if module == 'expense_classifier' and 'classification_report' in metrics:
            # Show only key metrics
            report = metrics['classification_report']
            print(f"   accuracy: {metrics['accuracy']:.2%}")
            print(f"   n_train: {metrics['n_train']}")
            print(f"   n_test: {metrics['n_test']}")
            print(f"   n_categories: {metrics['n_categories']}")
            
            # Show per-category accuracy
            print(f"   \n   Per-category F1-scores:")
            for cat_name, cat_metrics in report.items():
                if isinstance(cat_metrics, dict) and 'f1-score' in cat_metrics:
                    support = cat_metrics.get('support', 0)
                    if support > 0:  # Only show categories with test samples
                        print(f"      {cat_name}: {cat_metrics['f1-score']:.2%} (n={int(support)})")
        else:
            for key, value in metrics.items():
                print(f"   {key}: {value}")
        print()
    
    # Test predictions on sample transactions
    print("=" * 70)
    print("TESTING PREDICTIONS ON REAL DATA")
    print("=" * 70)
    print()
    
    # Test classifier
    print("🏷️  Expense Classifier Test (Random Sample):")
    classifier = ExpenseClassifier(model_path='../models/expense_classifier.pkl')
    
    test_samples = df[df['transaction_type'] == 'expense'].sample(n=min(10, len(df))).to_dict('records')
    correct = 0
    total = len(test_samples)
    
    for i, txn in enumerate(test_samples, 1):
        result = classifier.predict(txn['description'], txn['merchant'], txn['amount'])
        actual = txn['category']
        predicted = result['category']
        match = actual == predicted
        if match:
            correct += 1
        
        icon = "✅" if match else "❌"
        print(f"\n{i}. {icon} '{txn['description'][:40]}'")
        print(f"   Amount: {txn['amount']:.2f} | Date: {txn['transaction_date'].date()}")
        print(f"   Actual: {actual} | Predicted: {predicted} ({result['confidence']:.0%})")
        print(f"   Method: {result['method']}")
    
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n   Sample Accuracy: {correct}/{total} = {accuracy:.1f}%")
    
    # Test anomaly detector
    print("\n\n🔍 Anomaly Detector Test:")
    detector = AnomalyDetector()
    detector.load_model('../models/anomaly_detector.pkl')
    
    anomalies = detector.batch_detect(df.to_dict('records'))
    print(f"   Found {len(anomalies)} anomalies in dataset ({len(anomalies)/len(df)*100:.1f}%)")
    
    if anomalies:
        print("\n   Top 5 Flagged Anomalies:")
        for i, anom in enumerate(anomalies[:5], 1):
            print(f"\n   {i}. 🚨 {anom['description'][:40]}")
            print(f"      Amount: {anom['amount']:.2f} TND | Category: {anom['category']}")
            print(f"      Date: {anom['transaction_date']}")
            print(f"      Reason: {anom['explanation']}")
    
    print("\n\n✅ Training and testing complete!")
    print(f"📁 Models saved to: {os.path.abspath('../models')}")
    print("\n💡 Next steps:")
    print("   1. Run: python test_models.py")
    print("   2. Proceed to Phase 3: FastAPI Backend")


if __name__ == "__main__":
    import sys
    
    # Usage examples
    # python train_with_excel.py data/transactions.xlsx
    # python train_with_excel.py data/transactions.xlsx 5000
    
    if len(sys.argv) < 2:
        print("Usage: python train_with_excel.py <excel_path> [sample_size]")
        print("\nExample:")
        print("  python train_with_excel.py data/transactions.xlsx")
        print("  python train_with_excel.py data/transactions.xlsx 5000")
        print("\nNote: Requires openpyxl library (pip install openpyxl)")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        sys.exit(1)
    
    train_on_excel_data(excel_path, sample_size)
