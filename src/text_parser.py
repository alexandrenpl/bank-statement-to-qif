from typing import List, Dict
from datetime import datetime
import re

def extract_transactions_from_text(text_path: str) -> List[Dict]:
    """
    Extract transactions from a text file containing copy-pasted card statements.
    
    Args:
        text_path (str): Path to the text file containing transactions
        
    Returns:
        List[Dict]: List of transactions with date, description, and amount
    """
    transactions = []
    
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip empty lines and join multi-line entries
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    current_transaction = {}
    for line in cleaned_lines:
        try:
            # Try to find a date at the start of the line
            # This supports common date formats: DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD
            date_pattern = r'^(\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})'
            date_match = re.match(date_pattern, line)
            
            if date_match:
                # If we have a previous transaction, save it
                if current_transaction:
                    transactions.append(current_transaction)
                    current_transaction = {}
                
                # Start a new transaction
                date_str = date_match.group(1)
                # Convert date to standard format (YYYY-MM-DD)
                if re.match(r'\d{2}[-/]\d{2}[-/]\d{4}', date_str):
                    date = datetime.strptime(date_str.replace('/', '-'), '%d-%m-%Y')
                else:
                    date = datetime.strptime(date_str.replace('/', '-'), '%Y-%m-%d')
                
                # Extract description and amount from the rest of the line
                rest_of_line = line[date_match.end():].strip()
                
                # Try to find amount at the end of the line
                # This supports formats like: 123.45, -123.45, 123,45, -123,45
                amount_pattern = r'[-]?\d+[.,]\d{2}\s*$'
                amount_match = re.search(amount_pattern, rest_of_line)
                
                if amount_match:
                    amount_str = amount_match.group(0).strip().replace(',', '.')
                    description = rest_of_line[:amount_match.start()].strip()
                else:
                    # If no amount on this line, store what we have and continue
                    description = rest_of_line
                    amount_str = None
                
                current_transaction = {
                    'date': date.strftime('%Y-%m-%d'),
                    'description': description
                }
                
                if amount_str:
                    current_transaction['amount'] = float(amount_str)
            
            elif current_transaction and 'amount' not in current_transaction:
                # Look for amount in continuation lines
                amount_pattern = r'[-]?\d+[.,]\d{2}\s*$'
                amount_match = re.search(amount_pattern, line)
                
                if amount_match:
                    amount_str = amount_match.group(0).strip().replace(',', '.')
                    current_transaction['amount'] = float(amount_str)
                else:
                    # If this line doesn't contain an amount, append it to description
                    current_transaction['description'] = (
                        current_transaction['description'] + ' ' + line.strip()
                    ).strip()
        
        except (ValueError, AttributeError) as e:
            print(f"Error processing line: {line}. Error: {e}")
            continue
    
    # Don't forget to add the last transaction
    if current_transaction and 'amount' in current_transaction:
        transactions.append(current_transaction)
    
    return transactions

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python text_parser.py <text_file>")
        sys.exit(1)
        
    transactions = extract_transactions_from_text(sys.argv[1])
    for transaction in transactions:
        print(transaction) 