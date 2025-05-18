from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

class TransactionCategorizer:
    def __init__(self):
        self.model = Pipeline([
            ('vectorizer', TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,
                strip_accents='unicode'
            )),
            ('classifier', LogisticRegression(
                multi_class='ovr',
                max_iter=1000
            ))
        ])
        
    def train(self, training_data: List[Dict]) -> None:
        """
        Train the model using description-category pairs.
        
        Args:
            training_data (List[Dict]): List of dictionaries with 'description' and 'category' keys
        """
        descriptions = [item['description'] for item in training_data]
        categories = [item['category'] for item in training_data]
        
        self.model.fit(descriptions, categories)
    
    def predict(self, descriptions: List[str]) -> List[str]:
        """
        Predict categories for new descriptions.
        
        Args:
            descriptions (List[str]): List of transaction descriptions
            
        Returns:
            List[str]: Predicted categories
        """
        return self.model.predict(descriptions)
    
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