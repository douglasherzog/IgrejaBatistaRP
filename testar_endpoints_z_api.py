import requests
import json

def testar_endpoints_z_api():
    """Testa diferentes endpoints para encontrar o correto"""
    
    instance_id = '3F60D2A3DCDA511AC1C3EEE72DB67A6D'
    token = '096B93C78E1AD1E267ECDAC0'
    
    print('🔍 TESTE COMPLETO DE ENDPOINTS Z-API')
    print('=' * 50)
    
    # Testar diferentes endpoints de envio
    endpoints_teste = [
        f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text",
        f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-message",
        f"https://api.z-api.io/instances/{instance_id}/token/{token}/message",
        f"https://api.z-api.io/token/{token}/instances/{instance_id}/send-text",
        f"https://api.z-api.io/send-text/{token}/{instance_id}",
        f"https://api.z-api.io/instances/{instance_id}/send-text/{token}",
    ]
    
    payload = {
        "phone": "5551980214882",
        "message": "🧪 TESTE DE ENDPOINT - IBINOVI\n\nTestando diferentes endpoints da Z-API."
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    for i, endpoint in enumerate(endpoints_teste, 1):
        print(f"\n{i}️⃣ Testando: {endpoint}")
        print(f"   Payload: {payload}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ SUCESSO! Endpoint encontrado!")
                break
            elif response.status_code == 403:
                print("   ❌ Erro 403 - Token/Permissão")
            elif response.status_code == 404:
                print("   ❌ Erro 404 - Endpoint não encontrado")
            else:
                print(f"   ❌ Erro {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n🔧 VERIFICAÇÃO FINAL:")
    print("1. Acesse: https://z-api.io/")
    print("2. Verifique documentação da API")
    print("3. Confirme endpoint correto para envio")
    print("4. Verifique se precisa de headers especiais")
    
    # Testar sem headers especiais
    print(f"\n🧪 Teste sem headers especiais:")
    endpoint_base = f"https://api.z-api.io/instances/{instance_id}/token/{token}"
    
    try:
        response = requests.get(endpoint_base, timeout=5)
        print(f"   GET {endpoint_base}: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Instância acessível!")
            
            # Tentar descobrir endpoints disponíveis
            data = response.json()
            print(f"   Dados: {data}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    testar_endpoints_z_api()
