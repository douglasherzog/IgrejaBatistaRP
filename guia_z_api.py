"""
🚀 GUIA DE CONFIGURAÇÃO Z-API - PASSO A PASSO

PASSO 1: CADASTRAR NA Z-API
============================
1. Acesse: https://z-api.io/
2. Clique em "CADASTRAR-SE"
3. Preencha seus dados (email, senha, etc.)
4. Confirme seu email

PASSO 2: ESCOLHER PLANO
=======================
1. Após login, vá para "PLANOS"
2. Recomendo: "BÁSICO" - R$19,90/mês
3. Benefícios do plano básico:
   - ✅ Mensagens ilimitadas
   - ✅ WhatsApp conectado 24/7
   - ✅ Suporte em português
   - ✅ API completa

PASSO 3: CONECTAR WHATSAPP
===========================
1. No painel, clique em "MINHAS INSTÂNCIAS"
2. Clique em "ADICIONAR INSTÂNCIA"
3. Dê um nome (ex: "IBINOVI-WhatsApp")
4. Leia o QR Code com seu WhatsApp:
   - Abra WhatsApp > Configurações > WhatsApp Web
   - Escaneie o QR Code no painel Z-API
5. Aguarde conexão (status "CONECTADO")

PASSO 4: OBTER CREDENCIAIS
==========================
1. Na sua instância, clique em "DETALHES"
2. Anote esses dados:
   - INSTANCE ID: (ex: 123456789ABCDEF)
   - TOKEN: (ex: ABC123DEF456GHI789)

PASSO 5: CONFIGURAR NO CÓDIGO
=============================
Abra o arquivo: app/whatsapp_service.py

Na linha 19, substitua:
self.api_url = "https://api.z-api.io/instances/YOUR_INSTANCE/token/YOUR_TOKEN"

Por:
self.api_url = "https://api.z-api.io/instances/SEU_INSTANCE_ID/token/SEU_TOKEN"

PASSO 6: ATIVAR ENVIO REAL
===========================
No mesmo arquivo, linhas 79-83:

COMENTE esta linha:
# return True  # Simulação bem-sucedida

DESCOMENTE estas linhas:
response = requests.post(self.api_url, json=payload, headers=headers)
return response.status_code == 200

PASSO 7: TESTAR
===============
1. Salve o arquivo
2. Reinicie o servidor
3. Vá para: http://localhost:8002/admin/notificacoes/teste
4. Envie uma mensagem de teste

CUSTO E BENEFÍCIOS:
==================
💰 Custo: R$19,90/mês
✅ Ilimitado mensagens
✅ WhatsApp profissional 24/7
✅ Suporte português
✅ API estável

SUPORTE:
========
- Site: https://z-api.io/
- WhatsApp: (51) 98484-5400
- Email: suporte@z-api.io

PRONTO! Após esses passos, seu sistema enviará mensagens reais! 🎉
"""

print("🚀 CONFIGURAÇÃO Z-API - GUIA COMPLETO")
print("=" * 50)
print()
print("📋 PASSO 1: Cadastre-se em https://z-api.io/")
print("💰 PASSO 2: Escolha plano BÁSICO (R$19,90/mês)")
print("📱 PASSO 3: Conecte seu WhatsApp via QR Code")
print("🔑 PASSO 4: Obtenha INSTANCE ID e TOKEN")
print("⚙️  PASSO 5: Atualize app/whatsapp_service.py")
print("🚀 PASSO 6: Ative envio real (descomente código)")
print("🧪 PASSO 7: Teste envio real")
print()
print("📱 Suporte Z-API: (51) 98484-5400")
print("💬 WhatsApp profissional para sua igreja!")
