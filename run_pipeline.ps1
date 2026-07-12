$env:JAVA_HOME = "C:\PROGRA~1\ECLIPS~1\JDK-80~1.9-H"
$env:HADOOP_HOME = "C:\Hadoop\hadoop-3.3.6"
$env:PYSPARK_PYTHON = "python"
$env:PYSPARK_DRIVER_PYTHON = "python"
$env:Path += ";C:\Hadoop\hadoop-3.3.6\bin"

Write-Host "=========================================="
Write-Host "   Starting Enterprise SOC Pipeline"
Write-Host "=========================================="

Write-Host "1. Starting Company Website Simulator (Background)..."
Start-Process -FilePath "python" -ArgumentList "07_company_website.py"
Start-Sleep -Seconds 3 # Give it time to generate historical baseline if missing

Write-Host "2. Training ML Model on Website Baseline..."
python 03_train_ml_model.py

Write-Host "3. Starting Flume Live Ingestion..."
Start-Process -FilePath "cmd" -ArgumentList "/c `"C:\Flume\apache-flume-1.11.0-bin\bin\flume-ng.cmd`" agent -conf C:\Flume\apache-flume-1.11.0-bin\conf -confFile 02_flume_agent.conf -name LogAgent"

Write-Host "4. Starting Real-Time Streaming Analyzer..."
Start-Process -FilePath "python" -ArgumentList "04_stream_analyzer.py"

Write-Host "5. Starting Enterprise SOC Dashboard..."
Start-Process -FilePath "python" -ArgumentList "06_dashboard.py"

Write-Host "=========================================="
Write-Host "Pipeline is LIVE! Check your SOC Dashboard at http://localhost:5000"
Write-Host "Go to /register to create your Analyst Account."
Write-Host "=========================================="
