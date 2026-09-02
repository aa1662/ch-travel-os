# CH Travel OS 2.0 Launcher
$baseDir = "C:\Data\charlotte-ai-os-dev\ch-travel-os"
$serverScript = "$baseDir\tools\server.py"
Set-Location -Path $baseDir

# 優先尋找無黑視窗的 pythonw.exe，次選 python.exe 或 py.exe
$pythonExe = $null
foreach ($cmd in @("pythonw", "python", "py")) {
    $found = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
    if ($found) {
        $pythonExe = $found
        break
    }
}
if (-not $pythonExe) {
    $pythonExe = "python.exe"
}

# 檢查伺服器是否已在運行 (探測核心 API)
$serverReady = $false
try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8080/api/list-trips" -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
    if ($resp.StatusCode -eq 200) { $serverReady = $true }
} catch {
    $serverReady = $false
}

if (-not $serverReady) {
    # 啟動背景伺服器
    if ($pythonExe -match "pythonw") {
        Start-Process -FilePath $pythonExe -ArgumentList "`"$serverScript`"" -WorkingDirectory $baseDir
    } else {
        Start-Process -FilePath $pythonExe -ArgumentList "`"$serverScript`"" -WorkingDirectory $baseDir -WindowStyle Hidden
    }
    
    # 等待伺服器就緒 (最長 5 秒)
    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8080/api/list-trips" -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                $serverReady = $true
                break
            }
        } catch {}
    }
}

# 開啟視覺化編輯器與首頁 (正確 Portal 根路由)
Start-Process "http://127.0.0.1:8080/core/editor.html"
Start-Process "http://127.0.0.1:8080/index.html"

