import re
from typing import List, Dict
from datetime import datetime

def normalize_description(description: str) -> str:
    """
    Normaliza a descrição da transação para melhorar o matching.
    Remove variações comuns e mantém apenas informações relevantes.
    """
    # Converte para minúsculas
    text = description.lower()
    
    # Remove valores monetários (ex: "12,50", "12.50", "12,50 EUR")
    text = re.sub(r'\b\d+[.,]?\d*\s*(?:eur|euro|euros)?\b', '', text)
    
    # Remove datas (ex: "24/01/2024", "24-01-2024", "24.01.24")
    text = re.sub(r'\b\d{1,2}[-./]\d{1,2}[-./]\d{2,4}\b', '', text)
    
    # Remove números isolados mas mantém números que são parte de nomes
    # Ex: remove "24" mas mantém "continente24"
    text = re.sub(r'\b\d+\b', '', text)
    
    # Remove caracteres especiais mas mantém espaços
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normaliza espaços múltiplos
    text = ' '.join(text.split())
    
    return text.strip()

def extract_merchant(description: str) -> str:
    """
    Tenta extrair o nome do estabelecimento/comerciante da descrição.
    Útil para casos onde a descrição varia mas o estabelecimento é o mesmo.
    """
    # Lista de palavras comuns a remover
    common_words = {'compra', 'compras', 'pagamento', 'transferencia', 'movimento'}
    
    # Normaliza a descrição
    text = normalize_description(description)
    
    # Divide em palavras
    words = text.split()
    
    # Remove palavras comuns
    words = [w for w in words if w not in common_words]
    
    # Se sobrou algo, retorna a primeira palavra (geralmente o nome do estabelecimento)
    return words[0] if words else ''

def enrich_transaction(transaction: Dict) -> Dict:
    """
    Enriquece uma transação com features adicionais para melhorar a categorização.
    """
    enriched = transaction.copy()
    
    # Adiciona descrição normalizada
    enriched['normalized_description'] = normalize_description(transaction['description'])
    
    # Adiciona merchant (se possível extrair)
    enriched['merchant'] = extract_merchant(transaction['description'])
    
    # Adiciona features de data (se a data estiver disponível)
    if 'date' in transaction:
        try:
            date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            enriched['day_of_week'] = date.strftime('%A').lower()
            enriched['day_of_month'] = str(date.day)
            enriched['month'] = date.strftime('%B').lower()
        except:
            pass
    
    return enriched

def process_transactions(transactions: List[Dict]) -> List[Dict]:
    """
    Processa uma lista de transações, adicionando features úteis para categorização.
    """
    return [enrich_transaction(t) for t in transactions] 