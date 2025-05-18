import argparse
import os
from pdf_reader import extract_transactions as extract_from_pdf
from text_parser import extract_transactions_from_text
from qif_parser import extract_training_data
from trainer import TransactionCategorizer
from predictor import categorize_transactions
from qif_writer import write_qif

def process_single_file(input_file, qif_dir, output_qif, model_path):
    """Process a single input file and generate QIF output"""
    # Step 1: Extract transactions from input file
    print(f"\nProcessing {input_file}...")
    if input_file.lower().endswith('.pdf'):
        transactions = extract_from_pdf(input_file)
        source_type = "PDF"
    else:
        transactions = extract_transactions_from_text(input_file)
        source_type = "text file"
    print(f"Found {len(transactions)} transactions in {source_type}")
    
    # Step 2: Get training data from existing QIF files
    print("\nGathering training data from existing QIF files...")
    qif_files = [
        os.path.join(qif_dir, f)
        for f in os.listdir(qif_dir)
        if f.lower().endswith('.qif')
    ]
    training_data = extract_training_data(qif_files)
    print(f"Found {len(training_data)} training examples")
    
    # Step 3: Train or load the model
    print("\nTraining/loading the model...")
    categorizer = TransactionCategorizer()
    if os.path.exists(model_path):
        categorizer = TransactionCategorizer.load_model(model_path)
    else:
        categorizer.train(training_data)
        categorizer.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Step 4: Categorize new transactions
    print("\nCategorizing transactions...")
    categorized_transactions = categorize_transactions(transactions, model_path)
    
    return categorized_transactions

def main():
    parser = argparse.ArgumentParser(description='Process bank statements (PDF or text) and generate categorized QIF file')
    
    # Input methods group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--pdf', help='Path to the bank statement PDF')
    input_group.add_argument('--text', help='Path to the text file containing copy-pasted transactions')
    input_group.add_argument('--input-list', help='Path to a file containing list of input files and output QIF')
    
    # Other arguments
    parser.add_argument('qif_dir', help='Directory containing existing QIF files for training')
    parser.add_argument('output_qif', help='Path where to save the output QIF file', nargs='?')
    parser.add_argument('--model-path', default='transaction_model.joblib',
                      help='Path where to save/load the trained model')
    
    args = parser.parse_args()
    
    if args.input_list:
        # Read input files from configuration file
        with open(args.input_list, 'r') as f:
            files = [line.strip() for line in f if line.strip()]
        
        if len(files) < 2:
            print("Error: Input list file must contain at least one input file and one output file")
            return
            
        input_files = files[:-1]  # All but last file are inputs
        output_qif = files[-1]    # Last file is output
        
        all_transactions = []
        for input_file in input_files:
            transactions = process_single_file(input_file, args.qif_dir, output_qif, args.model_path)
            all_transactions.extend(transactions)
        
        # Write combined QIF file
        print(f"\nWriting combined QIF file to {output_qif}...")
        write_qif(all_transactions, output_qif)
        
        # Print summary
        print("\nSummary of all categorized transactions:")
        for transaction in all_transactions:
            print(f"{transaction['date']} - {transaction['description']} "
                  f"({transaction['amount']}) -> {transaction['category']}")
    else:
        # Process single file
        input_file = args.pdf if args.pdf else args.text
        if not args.output_qif:
            print("Error: output_qif is required when not using --input-list")
            return
            
        transactions = process_single_file(input_file, args.qif_dir, args.output_qif, args.model_path)
        
        # Write QIF file
        print(f"\nWriting QIF file to {args.output_qif}...")
        write_qif(transactions, args.output_qif)
        
        # Print summary
        print("\nSummary of categorized transactions:")
        for transaction in transactions:
            print(f"{transaction['date']} - {transaction['description']} "
                  f"({transaction['amount']}) -> {transaction['category']}")

if __name__ == "__main__":
    main() 