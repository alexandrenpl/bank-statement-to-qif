# Bank Statement to QIF Converter

Automatically convert bank statements (PDF or text) to QIF files with smart transaction categorization based on your historical data.

## Features

- Multiple Input Formats
  - PDF bank statements
  - Copy-pasted text from online banking
- Smart Categorization
  - Learns from your existing QIF files
  - Uses machine learning to categorize new transactions
  - Improves over time as you add more data
- QIF Export
  - Generates standard QIF files
  - Compatible with most financial software
  - Preserves all transaction details

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
├── extratos/           # Your bank statements (PDF or text)
│   ├── extrato1.pdf
│   ├── extrato2.pdf
│   └── ...
├── qif_historico/     # Directory with your historical QIF file(s)
│   └── historico.qif
└── qif_novos/         # Where new QIF files will be saved
```

### Processing Multiple Files

The easiest way to process multiple files is to create an input list file (e.g., `input_files.txt`) with the following format:
```
extratos/janeiro2024.pdf
extratos/fevereiro2024.pdf
extratos/marco2024.pdf
qif_novos/combinado2024.qif
```

Note: The last line should be the output QIF file where all transactions will be combined.

Then run:
```bash
python src/main.py --input-list input_files.txt qif_historico/
```

### Processing Single Files

You can also process files individually:

```bash
python src/main.py [--pdf ARQUIVO_PDF | --text ARQUIVO_TEXTO] DIRETORIO_QIF SAIDA_QIF [--model-path modelo.joblib]
```

Example with PDF:
```bash
python src/main.py --pdf extratos/maio2024.pdf qif_historico/ qif_novos/maio2024.qif
```

Example with text file:
```bash
python src/main.py --text extratos/junho2024.txt qif_historico/ qif_novos/junho2024.qif
```

Example using a pre-trained model:
```bash
python src/main.py --pdf extratos/maio2024.pdf qif_historico/ qif_novos/maio2024.qif --model-path modelo.joblib
```

### Training the Model Separately

If you want to train the model separately (optional), you can use:

```bash
python src/trainer.py modelo.joblib qif_historico/historico.qif
```

This will:
1. Read your historical QIF file(s)
2. Train a new model
3. Save it as `modelo.joblib`

You can then use this pre-trained model when processing statements by adding the `--model-path` parameter to the main command.

### Notes
- The model learns from your existing QIF files, so make sure your historical QIF file has correctly categorized transactions
- The more historical data you have, the better the categorization will be
- You can process multiple statements in sequence, and the model will improve over time
- Training the model separately is optional but can be useful if you want to:
  - Save time when processing multiple statements
  - Ensure consistent categorization across multiple runs
  - Experiment with different training data
- When using the input list feature, all transactions from the input files will be combined into a single output QIF file
