# CH Travel OS 2.0 Launcher
$baseDir = "C:\Data\charlotte-ai-os-dev\ch-travel-os"
$serverScript = "$baseDir\tools\server.py"
$healthUrl = "http://127.0.0.1:8080/api/list-trips"
$logDir = Join-Path $env:TEMP "ch-travel-os"
$stdoutLog = Join-Path $logDir "server.stdout.log"
$stderrLog = Join-Path $logDir "server.stderr.log"
Set-Location -Path $baseDir

# Run python.exe hidden and redirect output so the detached server keeps stable streams.
$pythonExe = $null
foreach ($cmd in @("python", "py")) {
    $found = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
    if ($found) {
        $pythonExe = $found
        break
    }
}
if (-not $pythonExe) {
    throw "Python 3 was not found. Add python.exe or py.exe to PATH."
}

function Test-ServerReady {
    try {
        $resp = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

$serverReady = Test-ServerReady

if (-not $serverReady) {
    # Replace an unhealthy listener only when it belongs to this project.
    $listeners = @(Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue)
    foreach ($ownerPid in ($listeners.OwningProcess | Sort-Object -Unique)) {
        $owner = Get-CimInstance Win32_Process -Filter "ProcessId = $ownerPid" -ErrorAction SilentlyContinue
        $isTravelServer = $owner.Name -like "python*.exe" -and
            $owner.CommandLine -and
            $owner.CommandLine.IndexOf($serverScript, [StringComparison]::OrdinalIgnoreCase) -ge 0

        if (-not $isTravelServer) {
            throw "Port 8080 is occupied by another process (PID $ownerPid)."
        }

        Stop-Process -Id $ownerPid -Force -ErrorAction Stop
    }

    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    $serverProcess = Start-Process -FilePath $pythonExe `
        -ArgumentList "`"$serverScript`"" `
        -WorkingDirectory $baseDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -PassThru

    # Wait up to 10 seconds for the API to become ready.
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        $serverReady = Test-ServerReady
        if ($serverReady) { break }
        if ($serverProcess.HasExited) { break }
    }
}

if (-not $serverReady) {
    throw "CH Travel OS server failed to start. Check $stderrLog and $stdoutLog."
}

# Open the portal first so the editor remains the foreground tab.
Start-Process "http://127.0.0.1:8080/index.html"
Start-Sleep -Milliseconds 600
Start-Process "http://127.0.0.1:8080/core/editor.html"
