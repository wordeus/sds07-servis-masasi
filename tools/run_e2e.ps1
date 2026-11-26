# E2E koşusu (Windows PowerShell): tools/run_e2e.sh betiğinin karşılığı (INSTALL.md §5).
#
# 1) Port boş mu? (Eski sunucu açık kalırsa testler eski kodla koşar, RSK-20.)
# 2) Geçici veritabanı + migrate + rastgele parolayla demo kullanıcılar
# 3) Sunucuyu DEBUG kapalı başlat (KRR-15), Hafta 2, 3 ve 4 senaryolarını koş
# 4) Sunucuyu kapat, portun boşaldığını doğrula, geçici veritabanını sil
#
# Kullanım: powershell -ExecutionPolicy Bypass -File tools\run_e2e.ps1 [-OutDir reports\e2e] [-Port 8765]
# Dosya BOM'lu UTF-8 kaydedilir; Windows PowerShell 5.1 BOM'suz dosyada Türkçe metni bozar (RSK-27).
param([string]$OutDir = "reports\e2e", [int]$Port = 8765)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Error "HATA: $Port portu kullanımda. Eski sunucuyu kapatın (RSK-20)."
    exit 3
}
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = (Resolve-Path $OutDir).Path
$Db = Join-Path ([System.IO.Path]::GetTempPath()) ("sds07-e2e-" + [guid]::NewGuid().ToString("N").Substring(0, 8) + ".sqlite3")
$env:DJANGO_SQLITE_PATH = $Db
$env:E2E_PASSWORD = "E2e-" + [guid]::NewGuid().ToString("N").Substring(0, 12) + "-Aa1"
& $Py manage.py migrate -v 0
& $Py manage.py seed_demo_users --password $env:E2E_PASSWORD | Out-Null
$env:DJANGO_DEBUG = "0"
$server = Start-Process -FilePath $Py -ArgumentList @("manage.py", "runserver", "127.0.0.1:$Port", "--noreload", "--insecure") `
    -PassThru -WindowStyle Hidden -RedirectStandardError (Join-Path $OutDir "server-stderr.txt")
$status = 0
try {
    $ready = $false
    for ($i = 0; $i -lt 60 -and -not $ready; $i++) {
        Start-Sleep -Milliseconds 500
        $ready = [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    }
    if (-not $ready) { throw "HATA: sunucu başlamadı" }
    $shots = Join-Path $OutDir "screenshots"
    $suites = @(
        @("e2e\week2_auth_roles.py", "e2e-results.json"),
        @("e2e\week3_tickets.py", "e2e-week3-results.json"),
        @("e2e\week4_workflow.py", "e2e-week4-results.json")
    )
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($suite in $suites) {
        $output = & $Py $suite[0] --base-url "http://127.0.0.1:$Port" --out-dir $shots --results-json (Join-Path $OutDir $suite[1]) 2>&1 | ForEach-Object { "$_" }
        if ($LASTEXITCODE -ne 0) { $status = 1 }
        foreach ($line in $output) { $lines.Add($line); Write-Output $line }
    }
    # Konsol çıktısı UTF-8 yazılır (Tee-Object UTF-16 yazar).
    [System.IO.File]::WriteAllLines((Join-Path $OutDir "e2e-output.txt"), $lines, (New-Object System.Text.UTF8Encoding($false)))
}
finally {
    Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Remove-Item $Db -ErrorAction SilentlyContinue
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Error "HATA: $Port portu hâlâ açık"
    exit 5
}
Write-Output "port $Port boş; durum: $status"
exit $status
