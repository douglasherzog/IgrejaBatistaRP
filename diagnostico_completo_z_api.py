"""
🔍 DIAGNÓSTICO COMPLETO - PROBLEMA Z-API

ERRO: "Client-Token null not allowed" (Status 403)
TOKEN: 096B93C78E1AD1E267ECDAC0
INSTANCE: 3F60D2A3DCDA511AC1C3EEE72DB67A6D

POSSÍVEIS CAUSAS:
1. Token está incorreto ou expirou
2. Instance ID está incorreto
3. Instância não está ativa
4. WhatsApp não está conectado
5. Plano Z-API expirou
6. Formato da requisição está errado

AÇÕES NECESSÁRIAS:
1. Verificar painel Z-API
2. Confirmar status da instância
3. Verificar se WhatsApp está conectado
4. Confirmar plano ativo
5. Obter credenciais corretas
"""

import requests

def diagnosticar_completo():
    print("🔍 DIAGNÓSTICO COMPLETO Z-API")
    print("=" * 50)
    
    # Credenciais atuais
    instance_id = '3F60D2A3DCDA511AC1C3EEE72DB67A6D'
    token = '096B93C78E1AD1E267ECDAC0'
    
    print(f"📋 CREDENCIAIS ATUAIS:")
    print(f"   Instance ID: {instance_id}")
    print(f"   Token: {token}")
    print()
    
    # Teste 1: Verificar instância sem token
    print("1️⃣ TESTE: Verificar instância (sem token)")
    try:
        url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/status"
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 403:
            print("   ❌ Token sendo rejeitado")
        elif response.status_code == 404:
            print("   ❌ Instância não encontrada")
        elif response.status_code == 200:
            print("   ✅ Instância encontrada")
            data = response.json()
            print(f"   Conectado: {data.get('connected')}")
            print(f"   Estado: {data.get('state')}")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()
    
    # Teste 2: Verificar formato do token
    print("2️⃣ TESTE: Verificar formato do token")
    print(f"   Token: '{token}'")
    print(f"   Tamanho: {len(token)} caracteres")
    print(f"   Apenas hex: {all(c in '0123456789ABCDEFabcdef' for c in token)}")
    
    if len(token) != 24:
        print(f"   ❌ Tamanho incorreto (deveria ser 24)")
    else:
        print(f"   ✅ Tamanho correto")
    
    print()
    
    # Teste 3: Verificar formato do instance ID
    print("3️⃣ TESTE: Verificar formato do Instance ID")
    print(f"   Instance ID: '{instance_id}'")
    print(f"   Tamanho: {len(instance_id)} caracteres")
    print(f"   Apenas hex: {all(c in '0123456789ABCDEFabcdef' for c in instance_id)}")
    
    if len(instance_id) != 32:
        print(f"   ❌ Tamanho incorreto (deveria ser 32)")
    else:
        print(f"   ✅ Tamanho correto")
    
    print()
    
    # Teste 4: Tentar diferentes endpoints
    print("4️⃣ TESTE: Tentar endpoints diferentes")
    
    endpoints = [
        f"/instances/{instance_id}/token/{token}/status",
        f"/instances/{instance_id}/token/{token}",
        f"/token/{token}/instances/{instance_id}/status"
    ]
    
    for endpoint in endpoints:
        url = f"https://api.z-api.io{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"      ✅ SUCESSO!")
                break
        except:
            print(f"   {endpoint}: Erro")
    
    print()
    print("🔧 RECOMENDAÇÕES:")
    print("1. Acesse https://z-api.io/")
    print("2. Verifique se sua instância está ATIVA")
    print("3. Confirme se o WhatsApp está CONECTADO")
    print("4. Verifique se seu plano está ATIVO")
    print("5. Copie o token EXATAMENTE como aparece no painel")
    print("6. Entre em contato com o suporte: (51) 98484-5400")

if __name__ == "__main__":
    diagnosticar_completo()
