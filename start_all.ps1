Write-Host "Starting Zookeeper..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-File .\start_zk.ps1" -WindowStyle Hidden

Start-Sleep -Seconds 5

Write-Host "Starting Apache Kafka Broker..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-File .\start_kafka.ps1" -WindowStyle Hidden

Start-Sleep -Seconds 5

Write-Host "Starting Target Website (Producer)..."
Start-Process -FilePath "python.exe" -ArgumentList "07_company_website.py" -WindowStyle Hidden

Write-Host "Starting AI Stream Analyzer (Consumer)..."
Start-Process -FilePath "python.exe" -ArgumentList "-u 04_stream_analyzer.py" -WindowStyle Hidden

Write-Host "Starting SOC Dashboard..."
Start-Process -FilePath "python.exe" -ArgumentList "06_dashboard.py" -WindowStyle Hidden

Write-Host "======================================================"
Write-Host " All systems are GO!"
Write-Host " Dashboard: http://localhost:5000"
Write-Host " Target Website: http://localhost:5001"
Write-Host "======================================================"
