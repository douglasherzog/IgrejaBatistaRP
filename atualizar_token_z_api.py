"""
🔧 ATUALIZADOR DE TOKEN Z-API

Use este script quando o token expirar ou for inválido.

COMO USAR:
1. Acesse https://z-api.io/
2. Vá em "Minhas Instâncias"
3. Copie o TOKEN atualizado
4. Execute: python atualizar_token_z_api.py
5. Cole o novo token quando solicitado
"""

import re

def atualizar_token():
    """Atualiza o token da Z-API"""
    
    print("🔧 ATUALIZADOR DE TOKEN Z-API")
    print("=" * 40)
    print()
    print("📱 PASSOS:")
    print("1. Acesse: https://z-api.io/")
    print("2. Faça login")
    print("3. Vá em 'Minhas Instâncias'")
    print("4. Clique na sua instância")
    print("5. Copie o TOKEN atualizado")
    print()
    
    token = input("🔑 Cole o NOVO TOKEN aqui: ").strip()
    
    if not token:
        print("❌ Token inválido!")
        return False
    
    # Atualizar arquivo
    arquivo = "app/whatsapp_service.py"
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrair instance ID da URL atual
        url_match = re.search(r'instances/([^/]+)/token/', conteudo)
        if url_match:
            instance_id = url_match.group(1)
            
            # Atualizar URL
            nova_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
            url_pattern = r'self\.api_url = ".*"'
            conteudo = re.sub(url_pattern, f'self.api_url = "{nova_url}"', conteudo)
            
            # Atualizar API key
            key_pattern = r'self\.api_key = ".*"'
            conteudo = re.sub(key_pattern, f'self.api_key = "{token}"', conteudo)
            
            # Salvar
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print("✅ Token atualizado com sucesso!")
            print(f"🌐 Nova URL: {nova_url}")
            print()
            print("🚀 PRÓXIMOS PASSOS:")
            print("1. Reinicie o servidor")
            print("2. Teste envio de mensagem")
            
            return True
        else:
            print("❌ Não foi possível encontrar o Instance ID")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}")
        return False

if __name__ == "__main__":
    atualizar_token()
