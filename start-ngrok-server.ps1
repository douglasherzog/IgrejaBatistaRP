# PocketDesk - IgrejaBatistaRP Auto Start
# Inicia o servidor FastAPI e o ngrok, monitora e reinicia se cairem.

$ProjectDir = "c:\Users\Usuario\CascadeProjects\IgrejaBatistaRP"
$LogDir = "$ProjectDir\logs"
New-Item -ItemType Directory -Path $LogDir -Force -ErrorAction SilentlyContinue | Out-Null

$ServerOut = "$LogDir\server.out.log"
$ServerErr = "$LogDir\server.err.log"
$NgrokOut = "$LogDir\ngrok.out.log"
$NgrokErr = "$LogDir\ngrok.err.log"
$StartupLog = "$LogDir\startup.log"

function Write-Log($Message) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    $line | Out-File $StartupLog -Append -Encoding utf8
    Write-Output $line
}

function Stop-ProjectProcesses() {
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path -like "*$ProjectDir*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

function Restore-Repository() {
    Set-Location $ProjectDir
    if (-not (Test-Path "app\main.py")) {
        Write-Log "ARQUIVOS DO PROJETO AUSENTES. Executando git restore para autocura."
        git restore .
    }
    git status --short | Out-File $StartupLog -Append -Encoding utf8
}

function Start-Server() {
    $proc = Start-Process -FilePath "$ProjectDir\venv\Scripts\python.exe" `
        -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8002" `
        -WorkingDirectory $ProjectDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $ServerOut `
        -RedirectStandardError $ServerErr `
        -PassThru
    return $proc
}

function Start-Ngrok() {
    $proc = Start-Process -FilePath "ngrok" `
        -ArgumentList "http 8002" `
        -WorkingDirectory $ProjectDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $NgrokOut `
        -RedirectStandardError $NgrokErr `
        -PassThru
    return $proc
}

function Update-LastUrl() {
    try {
        $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
        $url = ($tunnels.tunnels | Select-Object -First 1).public_url
        if ($url) {
            $url | Out-File "$LogDir\last-url.txt" -Encoding utf8
            Write-Log "URL publica: $url"
        }
    } catch {
        Write-Log "Nao foi possivel obter URL do ngrok."
    }
}

function Test-Health() {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8002/" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Test-NgrokApi() {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# --- inicializacao ---
Write-Log "Iniciando watchdog IgrejaBatistaRP."
Restore-Repository
Stop-ProjectProcesses

$ServerProcess = Start-Server
$NgrokProcess = Start-Ngrok
Start-Sleep -Seconds 8
Update-LastUrl

Write-Log "Servidor PID: $($ServerProcess.Id)"
Write-Log "Ngrok PID: $($NgrokProcess.Id)"

# --- watchdog ---
while ($true) {
    Start-Sleep -Seconds 30

    $serverAlive = $ServerProcess -and (-not $ServerProcess.HasExited)
    $ngrokAlive = $NgrokProcess -and (-not $NgrokProcess.HasExited)
    $healthOk = Test-Health
    $ngrokApiOk = Test-NgrokApi

    if (-not $serverAlive -or -not $healthOk) {
        Write-Log "SERVIDOR CAIOU. Reiniciando..."
        Stop-ProjectProcesses
        Restore-Repository
        $ServerProcess = Start-Server
        $NgrokProcess = Start-Ngrok
        Start-Sleep -Seconds 8
        Update-LastUrl
    }
    elseif (-not $ngrokAlive -or -not $ngrokApiOk) {
        Write-Log "NGROK CAIOU. Reiniciando..."
        if ($NgrokProcess -and (-not $NgrokProcess.HasExited)) { $NgrokProcess | Stop-Process -Force -ErrorAction SilentlyContinue }
        Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        $NgrokProcess = Start-Ngrok
        Start-Sleep -Seconds 8
        Update-LastUrl
    }
}
