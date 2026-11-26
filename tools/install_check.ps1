# TC-INST-01 (Windows): tools/install_check.sh betiğinin PowerShell karşılığı.
# Projenin temiz bir kopyasını geçici klasörde temiz sanal ortama kurar ve CI adımlarının
# yerel eşdeğerini koşar (INSTALL.md §2). Sonuç (BAŞARILI/BAŞARISIZ) günlüğün son satırındadır.
#
# Kullanım: powershell -ExecutionPolicy Bypass -File tools\install_check.ps1 <py-sürümü> <etiket> <günlük> [kaynak]
# Örnek:    powershell -ExecutionPolicy Bypass -File tools\install_check.ps1 3.13 windows-py313 reports\install-check-windows-py313.log
param(
    [Parameter(Mandatory = $true)][string]$PyVersion,
    [Parameter(Mandatory = $true)][string]$Label,
    [Parameter(Mandatory = $true)][string]$Log,
    [string]$Source = "."
)
$ErrorActionPreference = "Continue"
# Yönlendirilmiş çıktıda Türkçe karakterler için (RSK-25).
$env:PYTHONUTF8 = "1"
$Src = (Resolve-Path $Source).Path
$Log = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Log))
$Work = Join-Path ([System.IO.Path]::GetTempPath()) ("sds07-install-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
$script:Status = 0
$Lines = New-Object System.Collections.Generic.List[string]

function Write-Step([string]$Text) { $Lines.Add($Text) }
function Invoke-Step([string]$Exe, [string[]]$Arguments) {
    $output = & $Exe @Arguments 2>&1 | ForEach-Object { "$_" }
    foreach ($line in $output) { $Lines.Add($line) }
    if ($LASTEXITCODE -ne 0) { $script:Status = 1; $Lines.Add("!! çıkış kodu $LASTEXITCODE") }
}

Write-Step ("== TC-INST-01 [$Label] başlangıç (UTC): " + (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))
Write-Step "== kaynak: $(Split-Path (Split-Path $Src -Parent) -Leaf)\$(Split-Path $Src -Leaf) (venv, db, reports hariç) -> geçici klasör"
Write-Step "== işletim sistemi: $((Get-CimInstance Win32_OperatingSystem).Caption) $([System.Environment]::OSVersion.Version)"
& robocopy $Src $Work /E /NFL /NDL /NJH /NJS /NP /XD .venv reports .git __pycache__ .ruff_cache /XF db.sqlite3 .coverage | Out-Null
Push-Location $Work
try {
    Invoke-Step "py" @("-$PyVersion", "--version")
    Invoke-Step "py" @("-$PyVersion", "-m", "venv", ".venv")
    $Py = Join-Path $Work ".venv\Scripts\python.exe"
    Invoke-Step $Py @("-m", "pip", "install", "-q", "--upgrade", "pip")
    Write-Step "== pip install -r requirements-dev.txt"
    Invoke-Step $Py @("-m", "pip", "install", "-q", "-r", "requirements-dev.txt")
    Invoke-Step $Py @("-m", "pip", "freeze")
    Write-Step "== ruff format --check / ruff check"
    Invoke-Step $Py @("-m", "ruff", "format", "--check", ".")
    Invoke-Step $Py @("-m", "ruff", "check", ".")
    Write-Step "== manage.py check / makemigrations --check"
    Invoke-Step $Py @("manage.py", "check")
    Invoke-Step $Py @("manage.py", "makemigrations", "--check", "--dry-run")
    Write-Step "== migrate (temiz veritabanı)"
    Invoke-Step $Py @("manage.py", "migrate", "-v", "1")
    Write-Step "== test + coverage"
    New-Item -ItemType Directory -Force reports | Out-Null
    Invoke-Step $Py @("-m", "coverage", "run", "manage.py", "test", "--results-json", "reports\unit-results.json")
    $report = & $Py -m coverage report 2>&1 | ForEach-Object { "$_" }
    foreach ($line in ($report | Select-Object -Last 3)) { $Lines.Add($line) }
    Write-Step "== check --deploy (üretim profili)"
    $env:DJANGO_ENV = "production"
    $env:DJANGO_ALLOWED_HOSTS = "sds07.example"
    $env:DJANGO_SECRET_KEY = (& $Py -c "import secrets; print(secrets.token_urlsafe(50))")
    Invoke-Step $Py @("manage.py", "check", "--deploy", "--fail-level", "WARNING")
}
finally {
    Remove-Item Env:DJANGO_ENV, Env:DJANGO_ALLOWED_HOSTS, Env:DJANGO_SECRET_KEY -ErrorAction SilentlyContinue
    Pop-Location
    Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
}
$result = if ($script:Status -eq 0) { "BAŞARILI" } else { "BAŞARISIZ" }
Write-Step ("== bitiş (UTC): " + (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") + " | durum: $result")
New-Item -ItemType Directory -Force (Split-Path $Log -Parent) | Out-Null
[System.IO.File]::WriteAllLines($Log, $Lines, (New-Object System.Text.UTF8Encoding($false)))
exit $script:Status
