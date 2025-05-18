from typing import List, Dict
from datetime import datetime

def write_qif(transactions: List[Dict], output_path: str) -> None:
    """
    Write transactions to a QIF file.
    
    Args:
        transactions (List[Dict]): List of transactions with date, description, amount, and category
        output_path (str): Path where to save the QIF file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write('!Type:Bank\n')
        
        for transaction in transactions:
            # Convert date to QIF format (MM/DD/YYYY)
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            qif_date = date.strftime('%m/%d/%Y')
            
            # Write transaction
            f.write(f'D{qif_date}\n')  # Date
            f.write(f'T{transaction["amount"]}\n')  # Amount
            f.write(f'P{transaction["description"]}\n')  # Payee/description
            f.write(f'L{transaction["category"]}\n')  # Category
            f.write('^\n')  # End of transaction marker

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) != 3:
        print("Usage: python qif_writer.py <transactions_json> <output_qif>")
        sys.exit(1)
    
    transactions_file = sys.argv[1]
    output_path = sys.argv[2]
    
    # Load categorized transactions
    with open(transactions_file, 'r', encoding='utf-8') as f:
        transactions = json.load(f)
    
    # Write QIF file
    write_qif(transactions, output_path)
    print(f"QIF file written to {output_path}") 