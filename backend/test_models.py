"""Quick test to validate trained models"""

from ai_modules.expense_classifier import ExpenseClassifier
from ai_modules.anomaly_detector import AnomalyDetector
from datetime import date

# Test 1: Expense Classifier
print("=" * 60)
print("TEST 1: Expense Classifier")
print("=" * 60)

classifier = ExpenseClassifier(model_path='../models/expense_classifier.pkl')

test_transactions = [
    ("Weekly groceries at Carrefour", "Carrefour"),
    ("Gas refill", "Shell"),
    ("Dinner with friends", "Restaurant La Belle"),
    ("Netflix subscription", "Netflix"),
    ("Doctor visit", "Clinic Central"),
]

for desc, merchant in test_transactions:
    result = classifier.predict(desc, merchant)
    print(f"\n'{desc}' at {merchant}")
    print(f"  → Category: {result['category']} ({result['confidence']:.0%} confidence)")
    print(f"  → Method: {result['method']}")
    print(f"  → Top 3: {[(c, f'{p:.0%}') for c, p in result['top_3_predictions']]}")

# Test 2: Anomaly Detector
print("\n" + "=" * 60)
print("TEST 2: Anomaly Detector")
print("=" * 60)

detector = AnomalyDetector()
detector.load_model('../models/anomaly_detector.pkl')

# Normal transaction
normal_txn = {
    'id': 1,
    'transaction_date': date(2026, 2, 10),
    'amount': 150,
    'category': 'Groceries',
    'description': 'Weekly shopping'
}

# Anomalous transaction
anomaly_txn = {
    'id': 2,
    'transaction_date': date(2026, 2, 11),
    'amount': 1500,  # Very high!
    'category': 'Shopping',
    'description': 'Electronics purchase'
}

historical = [
    {'transaction_date': date(2026, 1, i), 'amount': 150, 'category': 'Groceries', 'description': 'Shopping'}
    for i in range(1, 30)
]

print("\n🟢 Testing NORMAL transaction (150 TND groceries):")
result_normal = detector.detect(normal_txn, historical)
print(f"  → Anomaly: {result_normal['is_anomaly']}")
print(f"  → Score: {result_normal['anomaly_score']:.3f}")
print(f"  → Type: {result_normal['anomaly_type']}")

print("\n🔴 Testing ANOMALOUS transaction (1500 TND shopping):")
result_anomaly = detector.detect(anomaly_txn, historical)
print(f"  → Anomaly: {result_anomaly['is_anomaly']}")
print(f"  → Score: {result_anomaly['anomaly_score']:.3f}")
print(f"  → Type: {result_anomaly['anomaly_type']}")
print(f"  → Explanation: {result_anomaly['explanation']}")

print("\n✅ All tests completed!")
