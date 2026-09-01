# CH Travel OS 2.0 Launcher
Set-Location -Path "C:\Data\charlotte-ai-os-dev\ch-travel-os"

$port = 8080
$isRunning = $false

try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", $port)
    $isRunning = $true
    $tcp.Close()
} catch {
    $isRunning = $false
}

if (-not $isRunning) {
    # 啟動 Python 伺服器在背景
    Start-Process -FilePath "python" -ArgumentList "tools/server.py" -WorkingDirectory "C:\Data\charlotte-ai-os-dev\ch-travel-os" -WindowStyle Minimized
    Start-Sleep -Seconds 2
}

# 開啟瀏覽器
Start-Process "http://127.0.0.1:8080/core/editor.html"
Start-Process "http://127.0.0.1:8080/docs/index.html"
