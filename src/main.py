import argparse
import os
from training_pairs import extract_all_training_pairs, find_training_pairs
from pdf_reader import extract_transactions as extract_from_pdf
from qif_writer import write_qif

def train_and_process(training_pdf: str, training_qif: str, new_pdf: str, output_qif: str):
    """
    Treina o sistema usando um par PDF-QIF conhecido e processa um novo PDF.
    
    Args:
        training_pdf: PDF de treinamento com transações conhecidas
        training_qif: QIF correspondente ao PDF de treinamento
        new_pdf: Novo PDF para processar
        output_qif: Onde salvar o QIF gerado
    """
    print(f"\nFase 1: Treinamento com {training_pdf} e {training_qif}")
    # Encontra pares de treinamento
    training_pairs = find_training_pairs(training_pdf, training_qif)
    print(f"Encontrados {len(training_pairs)} pares de treinamento")
    
    print(f"\nFase 2: Processando novo arquivo {new_pdf}")
    # Extrai transações do novo PDF
    new_transactions = extract_from_pdf(new_pdf)
    print(f"Encontradas {len(new_transactions)} transações no novo PDF")
    
    print("\nFase 3: Mapeando transações para formato QIF")
    # Para cada nova transação, encontra o par de treinamento mais similar
    mapped_transactions = []
    for trans in new_transactions:
        best_match = None
        best_score = 0.7  # threshold mínimo para considerar um match
        
        for pdf_train, qif_train in training_pairs:
            from training_pairs import match_transactions
            score = match_transactions(trans, pdf_train)
            if score > best_score:
                best_score = score
                best_match = qif_train
        
        if best_match:
            # Usa os campos do QIF de treinamento, mas mantém data e valor da nova transação
            qif_trans = best_match.copy()
            qif_trans['date'] = trans['date']
            qif_trans['amount'] = trans['amount']
            mapped_transactions.append(qif_trans)
        else:
            # Se não encontrou match, usa a transação original sem categoria
            mapped_transactions.append(trans)
    
    print("\nFase 4: Gerando arquivo QIF")
    write_qif(mapped_transactions, output_qif)
    print(f"QIF gerado em {output_qif}")
    
    return mapped_transactions

def process_multiple_files(input_list: str, training_pdf: str, training_qif: str):
    """
    Processa múltiplos PDFs usando um único par de treinamento.
    
    Args:
        input_list: Arquivo com lista de PDFs e QIF de saída
        training_pdf: PDF de treinamento
        training_qif: QIF de treinamento
    """
    # Lê a lista de arquivos
    with open(input_list, 'r') as f:
        files = [line.strip() for line in f if line.strip()]
    
    if len(files) < 2:
        raise ValueError("Input list deve conter pelo menos um PDF e um QIF de saída")
    
    input_pdfs = files[:-1]  # Todos exceto o último são PDFs de entrada
    output_qif = files[-1]   # Último arquivo é o QIF de saída
    
    # Processa cada PDF e combina os resultados
    all_transactions = []
    for pdf_file in input_pdfs:
        print(f"\nProcessando {pdf_file}...")
        transactions = train_and_process(
            training_pdf=training_pdf,
            training_qif=training_qif,
            new_pdf=pdf_file,
            output_qif=output_qif
        )
        all_transactions.extend(transactions)
    
    # Gera QIF final com todas as transações
    print(f"\nGerando QIF final com {len(all_transactions)} transações...")
    write_qif(all_transactions, output_qif)
    print(f"QIF final gerado em {output_qif}")

def main():
    parser = argparse.ArgumentParser(
        description='Converte extratos bancários PDF para QIF usando aprendizado supervisionado'
    )
    
    # Argumentos para o arquivo de treinamento
    parser.add_argument('--train-pdf', required=True,
                      help='PDF de treinamento com transações conhecidas')
    parser.add_argument('--train-qif', required=True,
                      help='QIF correspondente ao PDF de treinamento')
    
    # Grupo mutuamente exclusivo para entrada
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--pdf', help='Novo PDF para processar')
    input_group.add_argument('--input-list', 
                          help='Arquivo com lista de PDFs e QIF de saída')
    
    # Argumento opcional para saída (necessário apenas com --pdf)
    parser.add_argument('--output', help='Arquivo QIF de saída (necessário com --pdf)')
    
    args = parser.parse_args()
    
    if args.pdf and not args.output:
        parser.error("--output é necessário quando usando --pdf")
    
    if args.input_list:
        process_multiple_files(args.input_list, args.train_pdf, args.train_qif)
    else:
        train_and_process(args.train_pdf, args.train_qif, args.pdf, args.output)

if __name__ == "__main__":
    main() 