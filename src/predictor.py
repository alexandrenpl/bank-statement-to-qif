from typing import List, Dict
from trainer import TransactionCategorizer

def categorize_transactions(transactions: List[Dict], model_path: str) -> List[Dict]:
    """
    Categorize transactions using the trained model.
    
    Args:
        transactions (List[Dict]): List of transactions with 'description' field
        model_path (str): Path to the trained model file
        
    Returns:
        List[Dict]: Transactions with added 'category' field
    """
    # Load the model
    categorizer = TransactionCategorizer.load_model(model_path)
    
    # Extract descriptions
    descriptions = [t['description'] for t in transactions]
    
    # Predict categories
    categories = categorizer.predict(descriptions)
    
    # Add categories to transactions
    categorized_transactions = []
    for transaction, category in zip(transactions, categories):
        transaction_with_category = transaction.copy()
        transaction_with_category['category'] = category
        categorized_transactions.append(transaction_with_category)
    
    return categorized_transactions

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) != 3:
        print("Usage: python predictor.py <model_path> <transactions_json>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    transactions_file = sys.argv[2]
    
    # Load transactions from JSON file
    with open(transactions_file, 'r', encoding='utf-8') as f:
        transactions = json.load(f)
    
    # Categorize transactions
    categorized = categorize_transactions(transactions, model_path)
    
    # Print results
    for transaction in categorized:
        print(f"{transaction['date']} - {transaction['description']} - {transaction['amount']} -> {transaction['category']}") 