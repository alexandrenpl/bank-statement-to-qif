import pdfplumber
from typing import List, Dict
from datetime import datetime

def extract_transactions(pdf_path: str) -> List[Dict]:
    """
    Extract transactions from a PDF bank statement.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        List[Dict]: List of transactions with date, description, and amount
    """
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table from the page
            table = page.extract_table()
            if not table:
                continue
                
            for row in table:
                try:
                    # Skip header rows and empty rows
                    if not row or "Data" in str(row[0]):  # Adjust based on your PDF format
                        continue
                    
                    # Parse date, description and amount
                    # Adjust indices based on your PDF format
                    date_str = row[0].strip()
                    description = row[1].strip()
                    amount_str = row[2].strip().replace(",", ".")
                    
                    # Convert date string to datetime
                    date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                    
                    # Convert amount to float
                    amount = float(amount_str)
                    
                    transactions.append({
                        "date": date,
                        "description": description,
                        "amount": amount
                    })
                except (ValueError, IndexError, AttributeError) as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue
    
    return transactions

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_reader.py <pdf_path>")
        sys.exit(1)
        
    transactions = extract_transactions(sys.argv[1])
    for transaction in transactions:
        print(transaction) 