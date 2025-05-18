import argparse
import os
from pdf_reader import extract_transactions as extract_from_pdf
from text_parser import extract_transactions_from_text
from qif_parser import extract_training_data
from trainer import TransactionCategorizer
from predictor import categorize_transactions
from qif_writer import write_qif

def main():
    parser = argparse.ArgumentParser(description='Process bank statements (PDF or text) and generate categorized QIF file')
    
    # Input type group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--pdf', help='Path to the bank statement PDF')
    input_group.add_argument('--text', help='Path to the text file containing copy-pasted transactions')
    
    # Other arguments
    parser.add_argument('qif_dir', help='Directory containing existing QIF files for training')
    parser.add_argument('output_qif', help='Path where to save the output QIF file')
    parser.add_argument('--model-path', default='transaction_model.joblib',
                      help='Path where to save/load the trained model')
    
    args = parser.parse_args()
    
    # Step 1: Extract transactions from input file
    print("Extracting transactions from input file...")
    if args.pdf:
        transactions = extract_from_pdf(args.pdf)
        source_type = "PDF"
    else:
        transactions = extract_transactions_from_text(args.text)
        source_type = "text file"
    print(f"Found {len(transactions)} transactions in {source_type}")
    
    # Step 2: Get training data from existing QIF files
    print("\nGathering training data from existing QIF files...")
    qif_files = [
        os.path.join(args.qif_dir, f)
        for f in os.listdir(args.qif_dir)
        if f.lower().endswith('.qif')
    ]
    training_data = extract_training_data(qif_files)
    print(f"Found {len(training_data)} training examples")
    
    # Step 3: Train the model
    print("\nTraining the model...")
    categorizer = TransactionCategorizer()
    categorizer.train(training_data)
    categorizer.save_model(args.model_path)
    print(f"Model saved to {args.model_path}")
    
    # Step 4: Categorize new transactions
    print("\nCategorizing transactions...")
    categorized_transactions = categorize_transactions(transactions, args.model_path)
    
    # Step 5: Write QIF file
    print("\nWriting QIF file...")
    write_qif(categorized_transactions, args.output_qif)
    print(f"QIF file written to {args.output_qif}")
    
    # Print summary
    print("\nSummary of categorized transactions:")
    for transaction in categorized_transactions:
        print(f"{transaction['date']} - {transaction['description']} "
              f"({transaction['amount']}) -> {transaction['category']}")

if __name__ == "__main__":
    main() 