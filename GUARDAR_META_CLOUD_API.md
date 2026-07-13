# 🚀 Guia Meta Cloud API - WhatsApp Oficial (Gratuito)

A **Meta Cloud API** é a API oficial do WhatsApp. É a solução mais confiável para envio de mensagens em produção.

---

## ✅ Vantagens

- ✅ **API oficial** do WhatsApp/Meta
- ✅ **Até 1.000 conversas/mês gratuitas**
- ✅ **Não precisa de servidor ligado 24/7**
- ✅ **Mais confiável** que soluções não oficiais
- ✅ **Suporte a templates verificados**

---

## 📋 Pré-requisitos

1. **Conta de Desenvolvedor Meta**: https://developers.facebook.com/
2. **Página do Facebook** para a igreja
3. **Conta Business Verificada** (obrigatória para enviar mensagens)
4. **Número de telefone** para usar como remetente

---

## 🛠️ Passo a Passo

### 1️⃣ Criar Aplicativo no Meta Developers

1. Acesse: https://developers.facebook.com/apps/
2. Clique em **Criar Aplicativo**
3. Tipo: **Empresa**
4. Preencha os dados da igreja

### 2️⃣ Adicionar Produto WhatsApp

1. No painel do aplicativo, clique em **Adicionar Produto**
2. Selecione **WhatsApp**
3. Vá para a seção **Primeiros Passos da API**

### 3️⃣ Obter Phone Number ID e Access Token

No painel do WhatsApp:

- **Phone Number ID**: algo como `123456789012345`
- **Access Token**: clique em **Gerar Token de Acesso** (precisa de permissões `whatsapp_messaging`)

> ⚠️ O token expira em 60 dias. Para produção, use **Token Permanente** ou sistema de refresh.

### 4️⃣ Verificar Conta Business

Para enviar mensagens para números não autorizados, a conta precisa estar **verificada**:

1. Acesse: https://business.facebook.com/settings/
2. Envie documentos da igreja (CNPJ, contrato social, etc.)
3. Aguarde aprovação (geralmente 1-3 dias úteis)

### 5️⃣ Registrar Número de Telefone

1. No painel do WhatsApp, vá em **Configuração > Números de telefone**
2. Adicione o número que enviará as mensagens
3. Complete a verificação por SMS

### 6️⃣ Configurar o Sistema

Copie o `.env.example` para `.env`:

```bash
copy .env.example .env
```

Edite o `.env` com os dados da Meta:

```env
WHATSAPP_PROVIDER=meta-cloud
META_API_VERSION=v18.0
META_PHONE_NUMBER_ID=123456789012345
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER=5551999999999
```

### 7️⃣ Autorizar Números de Destino (Teste)

Para testar antes da verificação completa:

1. No painel Meta, vá em **Teste**
2. Adicione o número de telefone de destino (ex: 51980214882)
3. Envie uma mensagem para iniciar a conversa

> A Meta só permite enviar mensagens para números que enviaram mensagem primeiro OU números autorizados no modo teste.

### 8️⃣ Testar Envio

Execute o script de teste:

```bash
venv\Scripts\python.exe testar_meta_cloud.py
```

Ou acesse o painel:

```
http://localhost:8002/admin/notificacoes/teste
```

---

## 💰 Custos

- **Até 1.000 conversas iniciadas pelo usuário/mês**: GRÁTIS
- **Mensagens iniciadas pela empresa**: também contam no limite gratuito
- **Acima de 1.000 conversas**: tarifas por região
- Consulte: https://business.whatsapp.com/products/business-platform/pricing

---

## 📱 Comando para Teste Manual

```bash
curl -X POST "https://graph.facebook.com/v18.0/SEU_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "5551980214882",
    "type": "text",
    "text": {"body": "🧪 Teste Meta Cloud API - IBINOVI"}
  }'
```

---

## ⚠️ Limitações Importantes

1. **Conversas iniciadas pela empresa**: precisam usar **templates aprovados** se o usuário não respondeu nas últimas 24 horas.
2. **Números precisam ter WhatsApp Business API ou WhatsApp comum**: funciona para ambos.
3. **Verificação business**: obrigatória para uso em produção.
4. **Token**: renovar a cada 60 dias ou usar token permanente.

---

## 🎉 Pronto!

Com a Meta Cloud API você tem a solução mais confiável e oficial do WhatsApp integrada ao sistema! 🚀
