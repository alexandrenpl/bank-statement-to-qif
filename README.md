# Bank Statement to QIF Converter

Convert bank statements from PDF to QIF format using supervised learning from existing PDF-QIF pairs.

## Features

- PDF to QIF Conversion
  - Process bank statements in PDF format
  - Support for multiple bank accounts
  - Batch processing of multiple statements
- Supervised Learning Approach
  - Learn from existing PDF-QIF pairs
  - Match transactions based on dates, amounts, and descriptions
  - Support multiple PDF statements mapped to a single QIF file per bank account
- Smart Transaction Matching
  - Weighted scoring system for accurate matching
  - Preserves original transaction details
  - Handles various date and amount formats
- QIF Export
  - Generates standard QIF files
  - Compatible with most financial software
  - Maintains transaction integrity

## Setup

1. Create a conda environment:
```bash
conda create -n bank_processor python=3.11
conda activate bank_processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Directory Structure
Organize your files as follows:
```
your_working_directory/
├── statements/          # Your bank statements (PDF)
│   ├── account1/       # Statements for first account
│   │   ├── jan2024.pdf
│   │   ├── feb2024.pdf
│   │   └── ...
│   └── account2/       # Statements for second account
│       ├── jan2024.pdf
│       └── ...
├── training/           # Training QIF files (one per account)
│   ├── account1.qif
│   └── account2.qif
└── output/            # Where new QIF files will be saved
```

### Processing Multiple Files

Create an input list file (e.g., `input_files.txt`) with the following format:
```
# Training files (PDF and QIF pair)
statements/account1/dec2023.pdf
training/account1.qif

# Files to process
statements/account1/jan2024.pdf
statements/account1/feb2024.pdf
statements/account1/mar2024.pdf
output/account1_q1_2024.qif
```

The file should contain:
1. Training section with:
   - Path to the training PDF statement
   - Path to the corresponding QIF file
2. Processing section with:
   - Paths to all PDF files to process
   - Path to the output QIF file (last line)

Then run:
```bash
python src/main.py --input-list input_files.txt
```

### Processing Single Files

For individual files:

```bash
python src/main.py --train-pdf TRAINING_PDF --train-qif TRAINING_QIF --pdf NEW_PDF --output OUTPUT_QIF
```

Example:
```bash
python src/main.py --train-pdf statements/account1/dec2023.pdf --train-qif training/account1.qif --pdf statements/account1/jan2024.pdf --output output/jan2024.qif
```

### Transaction Matching

The system uses a sophisticated matching algorithm that considers:
- Transaction dates (weight: 3)
- Transaction amounts (weight: 3)
- Transaction descriptions (weight: 2)

A match is considered valid when the similarity score exceeds 0.7 (70% similarity).

### Notes
- Each bank account should have its own training QIF file
- Multiple PDF statements can be mapped to a single training QIF
- The system preserves original transaction dates and amounts
- Categories and other metadata are copied from the best matching transaction in the training data
- If no match is found for a transaction, it will be included without categorization
- The system supports various date formats and handles different amount representations
- All processing is done locally - no data is sent to external services

## Error Handling

- Invalid PDFs or unreadable files will be reported with appropriate error messages
- Transactions without matches will be included in the output but flagged
- Processing continues even if some transactions can't be matched
- Detailed logs help identify any issues during processing
