import requests
import json
from app.whatsapp_service import whatsapp_service
from app.database import SessionLocal
from app.models import Membro
from app.utils.telefone import formatar_telefone_exibicao

def diagnosticar_z_api():
    """Diagnóstico completo da API Z-API"""
    
    print("🔍 DIAGNÓSTICO COMPLETO Z-API")
    print("=" * 50)
    
    # 1. Verificar configuração
    print("1️⃣ CONFIGURAÇÃO DA API:")
    print(f"   URL: {whatsapp_service.api_url}")
    print(f"   Key: {whatsapp_service.api_key[:10]}...")
    
    # 2. Verificar status da instância
    print("\n2️⃣ STATUS DA INSTÂNCIA Z-API:")
    try:
        # Extrair instance ID da URL
        instance_id = whatsapp_service.api_url.split('/')[4]
        token = whatsapp_service.api_url.split('/')[6]
        
        status_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/status"
        
        response = requests.get(status_url)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"   Conectado: {'✅ SIM' if status_data.get('connected') else '❌ NÃO'}")
            print(f"   Número: {status_data.get('phone', 'N/A')}")
            print(f"   Estado: {status_data.get('state', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {e}")
    
    # 3. Verificar número do Douglas
    print("\n3️⃣ VERIFICAÇÃO DO NÚMERO:")
    db = SessionLocal()
    try:
        douglas = db.query(Membro).filter(Membro.nome.like('%Douglas%')).first()
        if douglas:
            print(f"   Nome: {douglas.nome}")
            print(f"   Telefone no banco: {douglas.telefone}")
            print(f"   Exibição: {formatar_telefone_exibicao(douglas.telefone)}")
            
            # Formatar para API
            telefone_api = whatsapp_service.formatar_telefone(douglas.telefone)
            print(f"   Formato API: {telefone_api}")
            
            # Verificar se o formato está correto
            if telefone_api == '5551980214882@c.us':
                print("   ✅ Formato correto para API")
            else:
                print(f"   ❌ Formato incorreto: {telefone_api}")
        else:
            print("   ❌ Douglas não encontrado")
    finally:
        db.close()
    
    # 4. Testar envio direto via API
    print("\n4️⃣ TESTE DIRETO DA API:")
    try:
        instance_id = whatsapp_service.api_url.split('/')[4]
        token = whatsapp_service.api_url.split('/')[6]
        
        # URL para enviar texto
        send_url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
        
        payload = {
            "phone": "5551980214882",
            "message": "🧪 TESTE DIRETO API Z-API\n\nMensagem de diagnóstico do sistema IBINOVI."
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"   Enviando para: 5551980214882")
        print(f"   URL: {send_url}")
        
        response = requests.post(send_url, json=payload, headers=headers)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('id'):
                print("   ✅ Mensagem enviada com sucesso!")
                print(f"   Message ID: {result.get('id')}")
            else:
                print("   ❌ Resposta inesperada")
        else:
            print("   ❌ Erro ao enviar mensagem")
            
    except Exception as e:
        print(f"   ❌ Erro no teste direto: {e}")
    
    print("\n5️⃣ POSSÍVEIS SOLUÇÕES:")
    print("   • Verifique se o WhatsApp está conectado no painel Z-API")
    print("   • Confirme se seu plano Z-API está ativo")
    print("   • Verifique se o número 51980214882 está salvo nos contatos")
    print("   • Tente enviar mensagem manualmente via painel Z-API")
    
    print("\n📱 SUPORTE Z-API:")
    print("   • WhatsApp: (51) 98484-5400")
    print("   • Site: https://z-api.io/")

if __name__ == "__main__":
    diagnosticar_z_api()
