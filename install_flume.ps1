$ErrorActionPreference = "Stop"

Write-Host "Fixing JAVA_HOME..."
$shortJavaHome = "C:\PROGRA~1\ECLIPS~1\JDK-80~1.9-H"
[Environment]::SetEnvironmentVariable("JAVA_HOME", $shortJavaHome, "User")
$env:JAVA_HOME = $shortJavaHome

Write-Host "Downloading Apache Flume..."
$flumeUrl = "https://archive.apache.org/dist/flume/1.11.0/apache-flume-1.11.0-bin.tar.gz"
$downloadPath = "C:\Users\Abhishek\Downloads\flume.tar.gz"
if (-Not (Test-Path $downloadPath)) {
    Invoke-WebRequest -Uri $flumeUrl -OutFile $downloadPath
}

Write-Host "Extracting Flume to C:\Flume..."
$flumeDir = "C:\Flume"
if (-Not (Test-Path $flumeDir)) {
    New-Item -ItemType Directory -Path $flumeDir | Out-Null
}
cd $flumeDir
tar -xf $downloadPath

$flumeHome = "C:\Flume\apache-flume-1.11.0-bin"
[Environment]::SetEnvironmentVariable("FLUME_HOME", $flumeHome, "User")

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notmatch "Flume") {
    $newPath = $currentPath + ";$flumeHome\bin"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Host "Flume installed successfully!"
