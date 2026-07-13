# 🚀 Guia WhatsApp Web.js - Servidor Local

Este guia explica como rodar um servidor WhatsApp local usando a biblioteca open-source **whatsapp-web.js**.

---

## ✅ O que é necessário

1. **Node.js** instalado (versão 18 ou superior)
2. **WhatsApp** no celular
3. Computador que ficará ligado para enviar mensagens

---

## 📥 Instalação do Node.js

1. Acesse: https://nodejs.org/
2. Baixe a versão **LTS** (recomendada)
3. Instale com as opções padrão
4. Verifique no terminal:

```bash
node --version
npm --version
```

---

## 📦 Instalação do Servidor

1. Abra o terminal na pasta `whatsapp-server`:

```bash
cd whatsapp-server
```

2. Instale as dependências:

```bash
npm install
```

Isso pode demorar alguns minutos na primeira vez.

---

## 🚀 Iniciar o Servidor

```bash
npm start
```

Você verá uma mensagem como:

```
🚀 IBINOVI WhatsApp Server
🌐 Endpoint: http://localhost:3001
⏳ Aguardando conexão do WhatsApp...
```

E depois um **QR Code** no terminal.

---

## 📱 Conectar o WhatsApp

1. Abra o WhatsApp no celular
2. Vá em **Configurações > Aparelhos conectados > Conectar aparelho**
3. Escaneie o QR Code que apareceu no terminal
4. Aguarde a mensagem:

```
✅ WhatsApp conectado e pronto para enviar mensagens!
```

---

## ⚙️ Configurar o Sistema FastAPI

O arquivo `.env` já deve estar configurado assim:

```env
WHATSAPP_PROVIDER=webhook
WHATSAPP_WEBHOOK_URL=http://localhost:3001/send-message
```

Se ainda não tiver o `.env`, copie do exemplo:

```bash
copy .env.example .env
```

---

## 🧪 Testar Envio

1. Certifique-se de que o servidor Node.js está rodando
2. Execute o teste:

```bash
venv\Scripts\python.exe testar_webhook_local.py
```

Ou acesse o painel:

```
http://localhost:8002/admin/notificacoes/teste
```

---

## 📡 Endpoints do Servidor

### Status
```bash
curl http://localhost:3001/status
```

### Enviar mensagem
```bash
curl -X POST http://localhost:3001/send-message \
  -H "Content-Type: application/json" \
  -d '{"number": "5551980214882", "message": "🧪 Teste IBINOVI"}'
```

---

## 🔄 Manter o Servidor Rodando

### Opção 1: Terminal aberto
Mantenha o terminal aberto com `npm start`.

### Opção 2: PM2 (recomendado para produção)
Instale o PM2 globalmente:

```bash
npm install -g pm2
pm2 start server.js --name ibinovi-whatsapp
pm2 save
pm2 startup
```

---

## ⚠️ Observações Importantes

1. **Computador precisa ficar ligado**: O servidor WhatsApp precisa estar rodando para enviar mensagens.
2. **WhatsApp permanece conectado**: A biblioteca usa `LocalAuth` para salvar a sessão, então geralmente não precisa escanear o QR Code toda vez.
3. **Número do celular**: Deve ter internet e WhatsApp ativo.
4. **Firewall**: Verifique se a porta `3001` está liberada para localhost.

---

## 🛠️ Problemas Comuns

### "Puppeteer não encontrado"
Instale o Chromium manualmente ou use:

```bash
npm install puppeteer
```

### QR Code não aparece
Reinicie o servidor e delete a pasta `.wwebjs_auth` para forçar nova autenticação.

### Mensagens não chegam
- Verifique se o número está correto (com DDI 55)
- Confirme se o WhatsApp está conectado via `/status`
- Verifique os logs do servidor

---

## 🎉 Pronto!

Seu sistema agora envia mensagens reais via WhatsApp Web usando uma solução open-source! 🚀
