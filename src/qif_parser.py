from typing import List, Dict
import os
from qifparse.parser import QifParser

def extract_training_data(qif_files: List[str]) -> List[Dict]:
    """
    Extract description-category pairs from existing QIF files for training.
    
    Args:
        qif_files (List[str]): List of paths to QIF files
        
    Returns:
        List[Dict]: List of description-category pairs
    """
    training_data = []
    
    for qif_file in qif_files:
        try:
            with open(qif_file, 'r', encoding='utf-8') as f:
                qif = QifParser.parse(f)
                
            for transaction in qif.get_transactions():
                if hasattr(transaction, 'category') and transaction.category:
                    training_data.append({
                        "description": transaction.memo or transaction.payee or "",
                        "category": transaction.category
                    })
        except Exception as e:
            print(f"Error processing {qif_file}: {e}")
            continue
    
    # Remove duplicates while preserving order
    seen = set()
    unique_data = []
    for item in training_data:
        key = (item['description'], item['category'])
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    
    return unique_data

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python qif_parser.py <qif_file1> [qif_file2 ...]")
        sys.exit(1)
        
    training_data = extract_training_data(sys.argv[1:])
    for entry in training_data:
        print(f"{entry['description']} -> {entry['category']}") 