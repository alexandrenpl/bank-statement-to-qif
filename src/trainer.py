from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
import joblib
from text_processor import process_transactions

class DescriptionTransformer(BaseEstimator, TransformerMixin):
    """Extrai e processa a descrição da transação"""
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return [item['normalized_description'] for item in X]

class MerchantTransformer(BaseEstimator, TransformerMixin):
    """Extrai o nome do estabelecimento"""
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return [item['merchant'] for item in X]

class DateFeatureTransformer(BaseEstimator, TransformerMixin):
    """Extrai features relacionadas à data"""
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        features = []
        for item in X:
            # Combina dia da semana, dia do mês e mês em uma string
            date_features = []
            if 'day_of_week' in item:
                date_features.append(item['day_of_week'])
            if 'day_of_month' in item:
                date_features.append(item['day_of_month'])
            if 'month' in item:
                date_features.append(item['month'])
            features.append(' '.join(date_features))
        return features

class TransactionCategorizer:
    def __init__(self):
        # Pipeline para processar descrições
        description_pipe = Pipeline([
            ('selector', DescriptionTransformer()),
            ('vectorizer', TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=10000,
                strip_accents='unicode',
                analyzer='char_wb',
                lowercase=True,
                min_df=2
            ))
        ])
        
        # Pipeline para processar merchants
        merchant_pipe = Pipeline([
            ('selector', MerchantTransformer()),
            ('vectorizer', TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,
                strip_accents='unicode'
            ))
        ])
        
        # Pipeline para processar datas
        date_pipe = Pipeline([
            ('selector', DateFeatureTransformer()),
            ('vectorizer', TfidfVectorizer(
                ngram_range=(1, 1)
            ))
        ])
        
        # Combina todas as features
        self.model = Pipeline([
            ('features', FeatureUnion([
                ('description', description_pipe),
                ('merchant', merchant_pipe),
                ('date', date_pipe)
            ])),
            ('classifier', LogisticRegression(
                multi_class='ovr',
                max_iter=1000,
                class_weight='balanced'
            ))
        ])
        
    def train(self, training_data: List[Dict]) -> None:
        """
        Train the model using description-category pairs.
        
        Args:
            training_data (List[Dict]): List of dictionaries with 'description' and 'category' keys
        """
        # Processa as transações para adicionar features
        processed_data = process_transactions(training_data)
        
        # Extrai as categorias
        categories = [item['category'] for item in training_data]
        
        # Treina o modelo
        self.model.fit(processed_data, categories)
    
    def predict(self, transactions: List[Dict]) -> List[str]:
        """
        Predict categories for new transactions.
        
        Args:
            transactions (List[Dict]): List of transactions with 'description' field
            
        Returns:
            List[str]: Predicted categories
        """
        # Processa as transações para adicionar features
        processed_data = process_transactions(transactions)
        
        return self.model.predict(processed_data)
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model to a file."""
        joblib.dump(self.model, filepath)
    
    @classmethod
    def load_model(cls, filepath: str) -> 'TransactionCategorizer':
        """Load a trained model from a file."""
        categorizer = cls()
        categorizer.model = joblib.load(filepath)
        return categorizer

if __name__ == "__main__":
    import sys
    from qif_parser import extract_training_data
    
    if len(sys.argv) < 3:
        print("Usage: python trainer.py <model_output_path> <qif_file1> [qif_file2 ...]")
        sys.exit(1)
    
    model_path = sys.argv[1]
    qif_files = sys.argv[2:]
    
    # Get training data
    training_data = extract_training_data(qif_files)
    
    if not training_data:
        print("No training data found in the provided QIF files")
        sys.exit(1)
    
    # Train model
    categorizer = TransactionCategorizer()
    categorizer.train(training_data)
    
    # Save model
    categorizer.save_model(model_path)
    print(f"Model saved to {model_path}") 