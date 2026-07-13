import requests
import json

def testar_payloads_z_api():
    """Testa diferentes formatos de payload para Z-API"""
    
    instance_id = '3F60D2A3DCDA511AC1C3EEE72DB67A6D'
    token = '096B93C78E1AD1E267ECDAC0'
    
    print('🔍 TESTE DE DIFERENTES PAYLOADS Z-API')
    print('=' * 50)
    
    # Testar diferentes formatos de payload
    payloads_teste = [
        {
            "nome": "Formato 1: phone + message",
            "payload": {
                "phone": "5551980214882",
                "message": "🧪 Teste formato 1 - IBINOVI"
            }
        },
        {
            "nome": "Formato 2: number + body",
            "payload": {
                "number": "5551980214882",
                "body": "🧪 Teste formato 2 - IBINOVI"
            }
        },
        {
            "nome": "Formato 3: phone + body",
            "payload": {
                "phone": "5551980214882",
                "body": "🧪 Teste formato 3 - IBINOVI"
            }
        },
        {
            "nome": "Formato 4: number + message",
            "payload": {
                "number": "5551980214882",
                "message": "🧪 Teste formato 4 - IBINOVI"
            }
        },
        {
            "nome": "Formato 5: com @c.us",
            "payload": {
                "phone": "5551980214882@c.us",
                "message": "🧪 Teste formato 5 - IBINOVI"
            }
        },
        {
            "nome": "Formato 6: com 55",
            "payload": {
                "phone": "5551980214882",
                "message": "🧪 Teste formato 6 - IBINOVI",
                "isGroup": False
            }
        }
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    for i, teste in enumerate(payloads_teste, 1):
        print(f"\n{i}️⃣ {teste['nome']}")
        print(f"   Payload: {teste['payload']}")
        
        # Testar endpoints diferentes
        endpoints = [
            f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text",
            f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-message",
            f"https://api.z-api.io/instances/{instance_id}/token/{token}/message"
        ]
        
        for j, endpoint in enumerate(endpoints, 1):
            endpoint_name = endpoint.split('/')[-1]
            print(f"   Testando {endpoint_name}...")
            
            try:
                response = requests.post(endpoint, json=teste['payload'], headers=headers, timeout=10)
                print(f"      Status: {response.status_code}")
                print(f"      Response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('id'):
                        print(f"      ✅ SUCESSO! ID: {result.get('id')}")
                        print(f"      🎯 Payload correto: {teste['nome']}")
                        print(f"      🎯 Endpoint correto: {endpoint}")
                        return True
                
            except Exception as e:
                print(f"      ❌ Erro: {e}")
    
    print(f"\n🔧 Nenhum formato funcionou. Verificar:")
    print(f"1. Documentação oficial Z-API")
    print(f"2. Se WhatsApp está conectado")
    print(f"3. Se plano está ativo")
    print(f"4. Contato suporte: (51) 98484-5400")
    
    return False

if __name__ == "__main__":
    testar_payloads_z_api()
