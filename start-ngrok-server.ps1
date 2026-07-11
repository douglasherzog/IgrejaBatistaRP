# PocketDesk - IgrejaBatistaRP Auto Start
# Inicia o servidor FastAPI e o ngrok automaticamente ao ligar o computador

$ProjectDir = "c:\Users\Usuario\CascadeProjects\IgrejaBatistaRP"
$LogDir = "$ProjectDir\logs"
New-Item -ItemType Directory -Path $LogDir -Force -ErrorAction SilentlyContinue | Out-Null

# Parar processos antigos para evitar conflito de portas
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and $_.Path -like "*$ProjectDir*"
} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Iniciar servidor FastAPI
$ServerOut = "$LogDir\server.out.log"
$ServerErr = "$LogDir\server.err.log"
$ServerProcess = Start-Process -FilePath "$ProjectDir\venv\Scripts\python.exe" `
    -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8002" `
    -WorkingDirectory $ProjectDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $ServerOut `
    -RedirectStandardError $ServerErr `
    -PassThru

Start-Sleep -Seconds 5

# Iniciar ngrok
$NgrokOut = "$LogDir\ngrok.out.log"
$NgrokErr = "$LogDir\ngrok.err.log"
$NgrokProcess = Start-Process -FilePath "ngrok" `
    -ArgumentList "http 8002" `
    -WorkingDirectory $ProjectDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $NgrokOut `
    -RedirectStandardError $NgrokErr `
    -PassThru

Start-Sleep -Seconds 5

# Gravar URL atual em arquivo para fácil consulta
try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $url = ($tunnels.tunnels | Select-Object -First 1).public_url
    if ($url) {
        $url | Out-File "$LogDir\last-url.txt"
        Write-Output "URL publica: $url"
    }
} catch {
    Write-Output "Nao foi possivel obter URL do ngrok. Verifique ngrok.log"
}

Write-Output "Servidor PID: $($ServerProcess.Id)"
Write-Output "Ngrok PID: $($NgrokProcess.Id)"
