from typing import List, Dict, Tuple
from pdf_reader import extract_transactions as extract_from_pdf
from qif_parser import extract_training_data
import difflib
from datetime import datetime
import re

def parse_date(date_str: str) -> datetime:
    """Tenta converter várias formatações de data para datetime"""
    formats = [
        '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%Y/%m/%d', '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Data não reconhecida: {date_str}")

def normalize_amount(amount_str: str) -> float:
    """Normaliza valores monetários para float"""
    # Remove símbolos de moeda e espaços
    amount = re.sub(r'[^\d,.-]', '', amount_str)
    # Converte para formato padrão com ponto decimal
    amount = amount.replace(',', '.')
    return float(amount)

def match_transactions(pdf_trans: Dict, qif_trans: Dict) -> float:
    """
    Calcula um score de similaridade entre duas transações.
    Retorna um valor entre 0 (completamente diferente) e 1 (match perfeito).
    """
    score = 0.0
    total_weight = 0.0
    
    # Compara datas (peso 3)
    try:
        pdf_date = parse_date(pdf_trans['date'])
        qif_date = parse_date(qif_trans['date'])
        if pdf_date == qif_date:
            score += 3
        total_weight += 3
    except ValueError:
        pass
    
    # Compara valores (peso 3)
    try:
        pdf_amount = normalize_amount(pdf_trans['amount'])
        qif_amount = normalize_amount(qif_trans['amount'])
        if abs(pdf_amount - qif_amount) < 0.01:  # tolerância de 1 centavo
            score += 3
        total_weight += 3
    except ValueError:
        pass
    
    # Compara descrições (peso 2)
    if 'description' in pdf_trans and 'description' in qif_trans:
        desc_similarity = difflib.SequenceMatcher(
            None, 
            pdf_trans['description'].lower(), 
            qif_trans['description'].lower()
        ).ratio()
        score += 2 * desc_similarity
        total_weight += 2
    
    return score / total_weight if total_weight > 0 else 0

def find_training_pairs(pdf_path: str, qif_path: str, threshold: float = 0.8) -> List[Tuple[Dict, Dict]]:
    """
    Encontra pares correspondentes entre transações do PDF e do QIF.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        qif_path: Caminho para o arquivo QIF
        threshold: Score mínimo para considerar um match (0-1)
    
    Returns:
        Lista de tuplas (transação_pdf, transação_qif) que correspondem entre si
    """
    # Extrai transações
    pdf_transactions = extract_from_pdf(pdf_path)
    qif_data = extract_training_data([qif_path])
    
    # Lista para armazenar os pares encontrados
    pairs = []
    used_qif = set()
    
    # Para cada transação do PDF, encontra o melhor match no QIF
    for pdf_trans in pdf_transactions:
        best_match = None
        best_score = threshold
        
        for i, qif_trans in enumerate(qif_data):
            if i in used_qif:
                continue
                
            score = match_transactions(pdf_trans, qif_trans)
            if score > best_score:
                best_score = score
                best_match = (i, qif_trans)
        
        if best_match:
            idx, qif_trans = best_match
            pairs.append((pdf_trans, qif_trans))
            used_qif.add(idx)
    
    return pairs

def extract_all_training_pairs(pdf_qif_pairs: List[Tuple[str, str]], threshold: float = 0.8) -> List[Tuple[Dict, Dict]]:
    """
    Extrai pares de treinamento de múltiplos arquivos PDF-QIF.
    
    Args:
        pdf_qif_pairs: Lista de tuplas (caminho_pdf, caminho_qif)
        threshold: Score mínimo para considerar um match
    
    Returns:
        Lista de todos os pares de treinamento encontrados
    """
    all_pairs = []
    
    for pdf_path, qif_path in pdf_qif_pairs:
        pairs = find_training_pairs(pdf_path, qif_path, threshold)
        all_pairs.extend(pairs)
    
    return all_pairs

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) != 4:
        print("Usage: python training_pairs.py <pdf_file> <qif_file> <output_json>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    qif_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # Encontra pares de treinamento
    pairs = find_training_pairs(pdf_path, qif_path)
    
    # Salva os pares em JSON para inspeção
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, indent=2, ensure_ascii=False)
    
    print(f"Encontrados {len(pairs)} pares de treinamento")
    print(f"Resultados salvos em {output_path}") 