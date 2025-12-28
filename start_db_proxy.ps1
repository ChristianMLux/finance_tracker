$port = 5432
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "Killing process on port $port..."
    Stop-Process -Id $process.OwningProcess -Force
}
./cloud_sql_proxy.exe fintracker-482613:europe-west3:fin-tracker-01
