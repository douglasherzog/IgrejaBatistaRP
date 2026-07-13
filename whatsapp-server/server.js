const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3001;

// Detecta Chrome instalado no sistema para evitar download do Chromium
function findChrome() {
  const possiblePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe')
  ];

  for (const chromePath of possiblePaths) {
    if (fs.existsSync(chromePath)) {
      console.log(`✅ Chrome encontrado: ${chromePath}`);
      return chromePath;
    }
  }

  console.warn('⚠️ Chrome não encontrado no sistema. Puppeteer tentará baixar Chromium.');
  return null;
}

const chromePath = findChrome();

// Cliente WhatsApp Web
const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: path.join(__dirname, '.wwebjs_auth')
  }),
  puppeteer: {
    headless: true,
    executablePath: chromePath || undefined,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run'
    ]
  }
});

let ready = false;
let qrCodeGenerated = false;

client.on('qr', async (qr) => {
  qrCodeGenerated = true;
  console.log('\n🔑 Escaneie o QR Code abaixo com seu WhatsApp:');
  console.log('   Abra WhatsApp > Configurações > Aparelhos conectados > Conectar aparelho\n');
  qrcodeTerminal.generate(qr, { small: true });

  try {
    const qrPath = path.join(__dirname, 'qr-code.png');
    await QRCode.toFile(qrPath, qr, {
      type: 'png',
      width: 400,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    });
    console.log(`\n🖼️  QR Code salvo como imagem: ${qrPath}`);
    console.log('   Abra o arquivo qr-code.png para escanear mais facilmente.\n');
  } catch (err) {
    console.error('❌ Erro ao salvar QR Code como imagem:', err);
  }
});

client.on('ready', () => {
  ready = true;
  qrCodeGenerated = false;
  console.log('\n✅ WhatsApp conectado e pronto para enviar mensagens!');
  console.log(`🌐 Servidor HTTP disponível em http://localhost:${PORT}\n`);
});

client.on('authenticated', () => {
  console.log('🔓 WhatsApp autenticado!');
});

client.on('auth_failure', (msg) => {
  console.error('❌ Falha na autenticação do WhatsApp:', msg);
  ready = false;
});

client.on('disconnected', (reason) => {
  console.log('⚠️ WhatsApp desconectado:', reason);
  ready = false;
  qrCodeGenerated = false;
});

// Inicializa o cliente
client.initialize();

// Formata número para o padrão WhatsApp
function formatNumber(number) {
  let cleaned = number.replace(/\D/g, '');
  if (!cleaned.startsWith('55')) {
    cleaned = '55' + cleaned;
  }
  return cleaned + '@c.us';
}

// Endpoint de status
app.get('/status', (req, res) => {
  res.json({
    ready,
    qrCodeGenerated,
    timestamp: new Date().toISOString()
  });
});

// Endpoint para enviar mensagem
app.post('/send-message', async (req, res) => {
  try {
    const { number, message } = req.body;

    if (!number || !message) {
      return res.status(400).json({
        success: false,
        error: 'number e message são obrigatórios'
      });
    }

    if (!ready) {
      return res.status(503).json({
        success: false,
        error: 'WhatsApp ainda não está conectado. Escaneie o QR Code primeiro.'
      });
    }

    const chatId = formatNumber(number);
    console.log(`📤 Enviando mensagem para ${chatId}...`);

    const response = await client.sendMessage(chatId, message);

    console.log(`✅ Mensagem enviada: ${response.id.id}`);

    res.json({
      success: true,
      messageId: response.id.id,
      chatId: chatId
    });
  } catch (error) {
    console.error('❌ Erro ao enviar mensagem:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check
app.get('/', (req, res) => {
  res.json({
    service: 'IBINOVI WhatsApp Server',
    status: ready ? 'ready' : 'not_ready',
    endpoints: {
      status: '/status',
      sendMessage: 'POST /send-message'
    }
  });
});

app.listen(PORT, () => {
  console.log(`\n🚀 IBINOVI WhatsApp Server`);
  console.log(`🌐 Endpoint: http://localhost:${PORT}`);
  console.log(`📊 Status: http://localhost:${PORT}/status`);
  console.log(`📤 Enviar mensagem: POST http://localhost:${PORT}/send-message`);
  console.log('\n⏳ Aguardando conexão do WhatsApp...\n');
});
