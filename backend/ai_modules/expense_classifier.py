"""
Expense Classification Module
- Rule-based categorization for common patterns
- ML fallback using TF-IDF + Logistic Regression
- Confidence scoring and explainability
"""

import re
import pickle
from typing import Dict, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


class ExpenseClassifier:
    """Hybrid rule-based + ML expense categorization"""
    
    # Rule-based patterns (high confidence)
    CATEGORY_RULES = {
        'Groceries': [
            r'\b(carrefour|monoprix|supermarket|grocery|market|food|hypermarket)\b',
            r'\b(fruits?|vegetables?|meat|dairy|bread|milk)\b'
        ],
        'Transport': [
            r'\b(uber|taxi|bus|metro|train|gas|fuel|parking|toll|shell|total|agil)\b',
            r'\b(car wash|vehicle|transport|gasoline|diesel)\b'
        ],
        'Dining': [
            r'\b(restaurant|cafe|coffee|pizza|burger|sushi|dining|gourmet|bar|pub)\b',
            r'\b(delivery|takeout|food delivery|glovo|talabat)\b'
        ],
        'Bills & Utilities': [
            r'\b(electricity|water|internet|phone|mobile|topnet|ooredoo|orange|steg|sonede)\b',
            r'\b(utility|utilities|bill|subscription|insurance)\b'
        ],
        'Healthcare': [
            r'\b(pharmacy|hospital|doctor|dentist|clinic|medical|health|medicine)\b',
            r'\b(drug store|prescription|treatment)\b'
        ],
        'Shopping': [
            r'\b(mall|store|shop|amazon|clothing|clothes|shoes|fashion|electronics)\b',
            r'\b(fnac|zara|h&m|nike|adidas)\b'
        ],
        'Entertainment': [
            r'\b(cinema|movie|theater|concert|game|gaming|spotify|netflix|youtube)\b',
            r'\b(gym|fitness|sport|entertainment|hobby)\b'
        ],
        'Education': [
            r'\b(school|university|course|book|books|education|tuition|library)\b',
            r'\b(training|learning|study|exam)\b'
        ],
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize classifier with optional pre-trained model"""
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words='english'
        )
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            multi_class='multinomial'
        )
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        if model_path:
            self.load_model(model_path)
    
    def _apply_rules(self, text: str) -> Tuple[Optional[str], float]:
        """
        Apply rule-based categorization
        
        Returns:
            (category, confidence) or (None, 0.0) if no match
        """
        text_lower = text.lower()
        
        for category, patterns in self.CATEGORY_RULES.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return category, 0.95  # High confidence for rule matches
        
        return None, 0.0
    
    def _prepare_text(self, description: str, merchant: Optional[str] = None) -> str:
        """Combine description and merchant for classification"""
        text = description or ""
        if merchant:
            text = f"{text} {merchant}"
        return text.strip()
    
    def train(self, transactions: list, categories: list) -> Dict:
        """
        Train the ML model
        
        Args:
            transactions: List of dicts with 'description', 'merchant', 'category'
            categories: List of category names
            
        Returns:
            Training metrics dict
        """
        # Prepare training data
        texts = []
        labels = []
        
        for txn in transactions:
            text = self._prepare_text(txn.get('description', ''), txn.get('merchant'))
            category = txn.get('category')
            
            if text and category:
                texts.append(text)
                labels.append(category)
        
        if len(texts) < 10:
            raise ValueError("Need at least 10 training samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Vectorize text
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model
        self.model.fit(X_train_vec, y_train_encoded)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test_encoded, y_pred)
        report = classification_report(
            y_test_encoded, y_pred, 
            target_names=self.label_encoder.classes_,
            output_dict=True
        )
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'n_train': len(X_train),
            'n_test': len(X_test),
            'n_categories': len(self.label_encoder.classes_)
        }
    
    def predict(
        self, 
        description: str, 
        merchant: Optional[str] = None,
        amount: Optional[float] = None
    ) -> Dict:
        """
        Predict category with confidence and explanation
        
        Returns:
            {
                'category': str,
                'confidence': float,
                'explanation': str,
                'method': 'rule' or 'ml',
                'top_3_predictions': [(category, confidence), ...]
            }
        """
        text = self._prepare_text(description, merchant)
        
        # Try rule-based first (high precision)
        rule_category, rule_confidence = self._apply_rules(text)
        if rule_category:
            return {
                'category': rule_category,
                'confidence': rule_confidence,
                'explanation': f"Matched rule-based pattern for '{rule_category}'",
                'method': 'rule',
                'top_3_predictions': [(rule_category, rule_confidence)]
            }
        
        # Fallback to ML model
        if not self.is_trained:
            return {
                'category': 'Other',
                'confidence': 0.5,
                'explanation': "Model not trained, using default category",
                'method': 'default',
                'top_3_predictions': [('Other', 0.5)]
            }
        
        try:
            # Vectorize and predict
            text_vec = self.vectorizer.transform([text])
            probabilities = self.model.predict_proba(text_vec)[0]
            predicted_idx = np.argmax(probabilities)
            confidence = probabilities[predicted_idx]
            category = self.label_encoder.classes_[predicted_idx]
            
            # Get top 3 predictions
            top_3_idx = np.argsort(probabilities)[-3:][::-1]
            top_3 = [
                (self.label_encoder.classes_[idx], probabilities[idx])
                for idx in top_3_idx
            ]
            
            # Generate explanation
            if confidence > 0.7:
                explanation = f"High confidence ML prediction based on text pattern"
            elif confidence > 0.5:
                explanation = f"Moderate confidence - consider verifying this categorization"
            else:
                explanation = f"Low confidence - manual review recommended"
            
            return {
                'category': category,
                'confidence': float(confidence),
                'explanation': explanation,
                'method': 'ml',
                'top_3_predictions': [(cat, float(conf)) for cat, conf in top_3]
            }
            
        except Exception as e:
            return {
                'category': 'Other',
                'confidence': 0.5,
                'explanation': f"Classification error: {str(e)}",
                'method': 'error',
                'top_3_predictions': [('Other', 0.5)]
            }
    
    def save_model(self, path: str):
        """Save trained model and vectorizer"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'label_encoder': self.label_encoder
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str):
        """Load pre-trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.is_trained = True


# Example usage
if __name__ == "__main__":
    # Demo training data
    training_data = [
        {'description': 'Weekly shopping', 'merchant': 'Carrefour', 'category': 'Groceries'},
        {'description': 'Gas refill', 'merchant': 'Shell', 'category': 'Transport'},
        {'description': 'Dinner', 'merchant': 'Pizza Restaurant', 'category': 'Dining'},
        {'description': 'Phone bill', 'merchant': 'Ooredoo', 'category': 'Bills & Utilities'},
        {'description': 'Medicine', 'merchant': 'Pharmacy Central', 'category': 'Healthcare'},
        {'description': 'New shoes', 'merchant': 'Nike Store', 'category': 'Shopping'},
        {'description': 'Movie tickets', 'merchant': 'Cinema Pathé', 'category': 'Entertainment'},
        {'description': 'Textbook', 'merchant': 'University Bookstore', 'category': 'Education'},
        # Add more samples...
    ]
    
    classifier = ExpenseClassifier()
    metrics = classifier.train(training_data, [])
    print(f"Training accuracy: {metrics['accuracy']:.2%}")
    
    # Test prediction
    result = classifier.predict("Coffee at Starbucks", "Starbucks")
    print(f"\nPrediction: {result['category']} (confidence: {result['confidence']:.2%})")
    print(f"Explanation: {result['explanation']}")
    print(f"Top 3: {result['top_3_predictions']}")
