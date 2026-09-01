# CH Travel OS 2.0 Launcher
$baseDir = "C:\Data\charlotte-ai-os-dev\ch-travel-os"
$serverScript = "$baseDir\tools\server.py"
Set-Location -Path $baseDir

# 尋找 python.exe
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) {
    $pythonExe = "python.exe"
}

# 檢查伺服器是否已在運行
$serverReady = $false
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8080/docs/index.html" -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
    if ($resp.StatusCode -eq 200) { $serverReady = $true }
} catch {
    $serverReady = $false
}

if (-not $serverReady) {
    Start-Process -FilePath $pythonExe -ArgumentList "`"$serverScript`"" -WorkingDirectory $baseDir -WindowStyle Minimized
    
    # 等待伺服器就緒 (最長 6 秒)
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8080/docs/index.html" -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $serverReady = $true
                break
            }
        } catch {}
    }
}

# 開啟視覺化編輯器與首頁
Start-Process "http://127.0.0.1:8080/core/editor.html"
Start-Process "http://127.0.0.1:8080/docs/index.html"
