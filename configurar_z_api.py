"""
🔧 CONFIGURADOR AUTOMÁTICO Z-API

Use este script após obter suas credenciais da Z-API.

COMO USAR:
1. Execute este script: python configurar_z_api.py
2. Digite seu INSTANCE ID quando solicitado
3. Digite seu TOKEN quando solicitado
4. O script atualizará o código automaticamente
5. Reinicie o servidor e teste!

EXEMPLO:
Instance ID: 123456789ABCDEF
Token: ABC123DEF456GHI789JKL012MNO345

URL gerada: https://api.z-api.io/instances/123456789ABCDEF/token/ABC123DEF456GHI789JKL012MNO345
"""

import os
import re

def configurar_z_api():
    """Configura automaticamente a API Z-API"""
    
    print("🔧 CONFIGURADOR AUTOMÁTICO Z-API")
    print("=" * 40)
    print()
    
    # Obter credenciais do usuário
    print("📱 Digite suas credenciais da Z-API:")
    print("(Você encontrou isso no painel z-api.io)")
    print()
    
    instance_id = input("🔑 INSTANCE ID: ").strip()
    token = input("🔐 TOKEN: ").strip()
    
    if not instance_id or not token:
        print("❌ Credenciais inválidas! Tente novamente.")
        return False
    
    # Construir URL
    api_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    
    print()
    print(f"🌐 URL gerada: {api_url}")
    print()
    
    # Atualizar arquivo whatsapp_service.py
    arquivo = "app/whatsapp_service.py"
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substituir URL da API
        url_pattern = r'self\.api_url = ".*"'
        nova_url = f'self.api_url = "{api_url}"'
        conteudo = re.sub(url_pattern, nova_url, conteudo)
        
        # Atualizar API key
        key_pattern = r'self\.api_key = ".*"'
        nova_key = f'self.api_key = "{token}"'
        conteudo = re.sub(key_pattern, nova_key, conteudo)
        
        # Ativar envio real (comentar simulação, descomentar API real)
        conteudo = conteudo.replace(
            'return True  # Simulação bem-sucedida - MUDAR PARA ENVIO REAL',
            '# return True  # Simulação bem-sucedida - MUDAR PARA ENVIO REAL'
        )
        
        conteudo = conteudo.replace(
            '# response = requests.post(self.api_url, json=payload, headers=headers)',
            'response = requests.post(self.api_url, json=payload, headers=headers)'
        )
        
        conteudo = conteudo.replace(
            '# return response.status_code == 200',
            'return response.status_code == 200'
        )
        
        # Salvar arquivo atualizado
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("✅ Configuração atualizada com sucesso!")
        print(f"📄 Arquivo atualizado: {arquivo}")
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Reinicie o servidor")
        print("2. Vá para: http://localhost:8002/admin/notificacoes/teste")
        print("3. Envie uma mensagem de teste")
        print("4. Verifique seu WhatsApp!")
        print()
        print("📱 Seu sistema agora envia mensagens reais! 🎉")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    except Exception as e:
        print(f"❌ Erro ao atualizar arquivo: {e}")
        return False

def verificar_configuracao_atual():
    """Verifica a configuração atual do WhatsApp"""
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO ATUAL")
    print("=" * 40)
    
    arquivo = "app/whatsapp_service.py"
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se está em modo simulação
        if "return True  # Simulação bem-sucedida" in conteudo:
            print("🔶 Status: MODO SIMULAÇÃO")
            print("📱 Mensagens não são enviadas para WhatsApp real")
        else:
            print("✅ Status: MODO REAL")
            print("📱 Mensagens são enviadas para WhatsApp real")
        
        # Verificar URL
        url_match = re.search(r'self\.api_url = "(.*?)"', conteudo)
        if url_match:
            url = url_match.group(1)
            if "YOUR_INSTANCE" in url or "YOUR_TOKEN" in url:
                print("🔶 URL: Credenciais padrão (precisa configurar)")
            else:
                print("✅ URL: Configurada com credenciais reais")
                print(f"🌐 {url}")
        
        print()
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verificar":
        verificar_configuracao_atual()
    else:
        configurar_z_api()
