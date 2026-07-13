import requests
import json

# Teste direto da API com as credenciais atuais
instance_id = '3F60D2A3DCDA511AC1C3EEE72DB67A6D'
token = '096B93C78E1AD1E267ECDAC0'

print('🔍 TESTE DIRETO DAS CREDENCIAIS')
print('=' * 40)

# Testar status
status_url = f'https://api.z-api.io/instances/{instance_id}/token/{token}/status'
print(f'📊 Verificando status...')
print(f'URL: {status_url}')

try:
    response = requests.get(status_url, timeout=10)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Conectado: {data.get("connected")}')
        print(f'📱 Número: {data.get("phone")}')
        print(f'📊 Estado: {data.get("state")}')
    else:
        print('❌ Erro ao verificar status')
        
except Exception as e:
    print(f'❌ Erro na requisição: {e}')

print()

# Testar envio de mensagem
send_url = f'https://api.z-api.io/instances/{instance_id}/token/{token}/send-text'
payload = {
    'phone': '5551980214882',
    'message': '🧪 TESTE DIRETO - IBINOVI\n\nMensagem de teste direto via API.'
}

print(f'📤 Testando envio direto...')
print(f'URL: {send_url}')
print(f'Payload: {payload}')

try:
    response = requests.post(send_url, json=payload, timeout=10)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('id'):
            print('✅ Mensagem enviada com sucesso!')
            print(f'📋 Message ID: {data.get("id")}')
        else:
            print('❌ Resposta sem ID')
    else:
        print('❌ Erro ao enviar mensagem')
        
except Exception as e:
    print(f'❌ Erro na requisição: {e}')
