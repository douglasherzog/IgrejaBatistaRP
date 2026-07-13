import re
from typing import Optional

def normalizar_telefone(telefone: str) -> Optional[str]:
    """
    Normaliza número de telefone para o formato padrão: 55DDDXXXXXXXX
    
    Args:
        telefone: Número de telefone em qualquer formato
        
    Returns:
        str: Número normalizado ou None se inválido
    """
    if not telefone:
        return None
    
    # Remove todos os caracteres não numéricos
    numeros = re.sub(r'\D', '', telefone)
    
    # Verifica se tem quantidade válida de dígitos
    if len(numeros) < 10 or len(numeros) > 13:
        return None
    
    # Remove o 9 adicional de números de celular (se tiver 11 dígitos sem DDI)
    if len(numeros) == 11 and not numeros.startswith('55'):
        # Formato: DDD + 9 + número (ex: 5199999999)
        ddd = numeros[:2]
        numero = numeros[2:]
        if numero.startswith('9'):
            numero = numero[1:]  # Remove o 9
        return f"55{ddd}{numero}"
    
    # Se já começa com 55 (Brasil)
    if numeros.startswith('55'):
        if len(numeros) == 12:  # 55 + DDD + 9 + número
            ddd = numeros[2:4]
            numero = numeros[4:]
            if numero.startswith('9'):
                numero = numero[1:]  # Remove o 9
            return f"55{ddd}{numero}"
        elif len(numeros) == 11:  # 55 + DDD + número (sem 9)
            return numeros
        elif len(numeros) == 13:  # 55 + DDD + 9 + número
            ddd = numeros[2:4]
            numero = numeros[4:]
            if numero.startswith('9'):
                numero = numero[1:]  # Remove o 9
            return f"55{ddd}{numero}"
    
    # Se não começa com 55 e tem 10 dígitos (DDD + número sem 9)
    if len(numeros) == 10:
        return f"55{numeros}"
    
    # Se não começa com 55 e tem 12 dígitos (DDI + DDD + número)
    if len(numeros) == 12:
        # Assume que é DDI 55 + DDD + número
        return numeros
    
    return None

def formatar_telefone_exibicao(telefone: str) -> str:
    """
    Formata número para exibição: (DDD) XXXXX-XXXX
    
    Args:
        telefone: Número normalizado (55DDDXXXXXXXX)
        
    Returns:
        str: Número formatado para exibição
    """
    if not telefone or len(telefone) < 12:
        return telefone
    
    # Remove o 55 (Brasil) se existir
    if telefone.startswith('55'):
        telefone = telefone[2:]
    
    if len(telefone) == 10:  # DDD + número
        ddd = telefone[:2]
        numero = telefone[2:]
        return f"({ddd}) {numero[:5]}-{numero[5:]}"
    
    return telefone

def validar_telefone(telefone: str) -> bool:
    """
    Valida se o número de telefone está no formato correto
    
    Args:
        telefone: Número de telefone
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not telefone:
        return False
    
    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', telefone)
    
    # Verifica se tem 12 dígitos (55 + DDD + número)
    return len(numeros) == 12 and numeros.startswith('55')

# Exemplos de uso e testes
def testar_normalizacao():
    """Testa a função de normalização com vários exemplos"""
    testes = [
        "5199999999",           # DDD + número (sem 9)
        "(51) 99999-9999",      # Formatado com 9
        "(51) 9999-9999",       # Formatado sem 9
        "555199999999",         # Com DDI e sem 9
        "5551999999999",        # Com DDI e com 9
        "+55 51 99999-9999",    # Com + e formatado
        "51 9999 9999",         # Espaços
        "51999999999",          # Com 9
        "9999-9999",            # Sem DDD
        "11999999999",          # DDD 11 com 9
        "(11) 99999-9999",      # São Paulo formatado
    ]
    
    print("🧪 Testes de Normalização de Telefone:")
    print("=" * 50)
    
    for teste in testes:
        normalizado = normalizar_telefone(teste)
        formatado = formatar_telefone_exibicao(normalizado) if normalizado else "INVÁLIDO"
        valido = validar_telefone(normalizado) if normalizado else False
        
        print(f"Original: {teste}")
        print(f"Normalizado: {normalizado}")
        print(f"Exibição: {formatado}")
        print(f"Válido: {'✅' if valido else '❌'}")
        print("-" * 30)

if __name__ == "__main__":
    testar_normalizacao()
