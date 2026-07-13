# 🚀 Guia Evolution API - WhatsApp Gratuito e Open-Source

A **Evolution API** é uma alternativa **gratuita e open-source** à Z-API. Ela é auto-hospedada (você instala no seu computador/servidor) e não cobra por mensagem.

---

## ✅ Vantagens

- 💰 **100% gratuita** (sem taxa por mensagem)
- 🔓 **Código aberto** (https://github.com/EvolutionAPI/evolution-api)
- 🏠 **Auto-hospedada** (você controla seus dados)
- 📱 **Conecta ao WhatsApp Web** (igual Z-API)
- 🚀 **API HTTP simples** (fácil integrar com FastAPI)

---

## 📋 Pré-requisitos

1. **Docker Desktop** instalado no Windows
   - Download: https://www.docker.com/products/docker-desktop
2. **Docker Compose** (já vem no Docker Desktop)
3. **WSL2** habilitado (Windows 10/11)

---

## 🛠️ Passo a Passo

### 1️⃣ Iniciar a Evolution API

No terminal, na pasta do projeto, execute:

```bash
docker-compose -f docker-compose.evolution.yml up -d
```

Isso vai baixar e iniciar o serviço na porta `8080`.

Aguarde cerca de 30-60 segundos para o serviço ficar pronto.

---

### 2️⃣ Criar uma Instância

A instância representa o WhatsApp conectado.

Execute no terminal (PowerShell):

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/instance/create" -Method Post -Headers @{"Content-Type"="application/json"; "apikey"="ibinovi_global_apikey"} -Body '{"instanceName": "ibinovi", "token": "ibinovi_instance_token", "qrcode": true, "integration": "WHATSAPP-BAILEYS"}'
```

Ou usando curl:

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: ibinovi_global_apikey" \
  -d '{"instanceName": "ibinovi", "token": "ibinovi_instance_token", "qrcode": true, "integration": "WHATSAPP-BAILEYS"}'
```

A resposta vai conter um **QR Code** em base64. Você precisa escanear com o WhatsApp do computador ou celular.

---

### 3️⃣ Conectar WhatsApp

1. Abra o WhatsApp no celular
2. Vá em **Configurações > Aparelhos conectados > Conectar aparelho**
3. Escaneie o QR Code retornado no passo 2
4. Aguarde o status mudar para **"open"**

Para verificar o status:

```bash
curl http://localhost:8080/instance/connectionState/ibinovi -H "apikey: ibinovi_global_apikey"
```

---

### 4️⃣ Configurar o Sistema FastAPI

Copie o arquivo `.env.example` para `.env`:

```bash
copy .env.example .env
```

Edite o `.env` e confirme:

```env
WHATSAPP_PROVIDER=evolution-api
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_INSTANCE_NAME=ibinovi
EVOLUTION_API_KEY=ibinovi_global_apikey
WHATSAPP_PHONE_NUMBER=5551999999999
```

> Se você mudou a `AUTHENTICATION_API_KEY` no docker-compose, use a mesma chave em `EVOLUTION_API_KEY`.

---

### 5️⃣ Reiniciar o Servidor FastAPI

```bash
# Parar servidor atual
Get-Process python | Stop-Process -Force

# Iniciar novamente com variáveis do .env
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

---

### 6️⃣ Testar Envio

Acesse o painel de testes:

```
http://localhost:8002/admin/notificacoes/teste
```

Ou execute o script de teste:

```bash
venv\Scripts\python.exe testar_evolution_api.py
```

---

## 🧪 Comandos Úteis

### Ver status da instância

```bash
curl http://localhost:8080/instance/connectionState/ibinovi -H "apikey: ibinovi_global_apikey"
```

### Listar instâncias

```bash
curl http://localhost:8080/instance/fetchInstances -H "apikey: ibinovi_global_apikey"
```

### Enviar mensagem manualmente

```bash
curl -X POST http://localhost:8080/message/sendText/ibinovi \
  -H "Content-Type: application/json" \
  -H "apikey: ibinovi_global_apikey" \
  -d '{"number": "5551980214882", "text": "🧪 Teste Evolution API - IBINOVI"}'
```

---

## 🛑 Parar o Serviço

```bash
docker-compose -f docker-compose.evolution.yml down
```

Para parar e remover dados:

```bash
docker-compose -f docker-compose.evolution.yml down -v
```

---

## 📱 Links Importantes

- **Repositório Evolution API**: https://github.com/EvolutionAPI/evolution-api
- **Documentação Oficial**: https://doc.evolution-api.com/
- **Docker Hub**: https://hub.docker.com/r/atendai/evolution-api

---

## ⚠️ Observações Importantes

1. **Computador precisa ficar ligado**: Como a Evolution API é auto-hospedada, o computador/servidor precisa estar ligado para enviar mensagens.
2. **WhatsApp Web conectado**: Mantenha o WhatsApp conectado na instância.
3. **Firewall**: Certifique-se de que a porta `8080` esteja liberada.
4. **Em produção**: Use PostgreSQL/Redis e uma chave API forte.

---

## 🎉 Pronto!

Com a Evolution API você terá um sistema de WhatsApp **gratuito, open-source e sob seu controle**! 🚀
