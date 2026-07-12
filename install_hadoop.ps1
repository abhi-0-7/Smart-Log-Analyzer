$ErrorActionPreference = "Stop"

$hadoopUrl = "https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz"
$hadoopDir = "C:\Hadoop"
$downloadPath = "C:\Users\Abhishek\Downloads\hadoop-3.3.6.tar.gz"

Write-Host "1. Downloading Hadoop 3.3.6 (This may take a few minutes)..."
if (-Not (Test-Path $downloadPath)) {
    Invoke-WebRequest -Uri $hadoopUrl -OutFile $downloadPath
}

Write-Host "2. Extracting Hadoop to C:\Hadoop..."
if (-Not (Test-Path $hadoopDir)) {
    New-Item -ItemType Directory -Path $hadoopDir | Out-Null
}

# Use native tar to extract
Write-Host "Extracting..."
cd C:\Hadoop
tar -xf $downloadPath
# It extracts into C:\Hadoop\hadoop-3.3.6. Let's move contents up one level or just use C:\Hadoop\hadoop-3.3.6 as HADOOP_HOME.
$hadoopHome = "C:\Hadoop\hadoop-3.3.6"

Write-Host "3. Downloading Windows Utilities (winutils.exe, hadoop.dll)..."
$binDir = "$hadoopHome\bin"
$winutilsUrl = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.2.2/bin/winutils.exe"
$hadoopDllUrl = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.2.2/bin/hadoop.dll"

Invoke-WebRequest -Uri $winutilsUrl -OutFile "$binDir\winutils.exe"
Invoke-WebRequest -Uri $hadoopDllUrl -OutFile "$binDir\hadoop.dll"
# Also copy hadoop.dll to system32 just in case
Copy-Item "$binDir\hadoop.dll" -Destination "C:\Windows\System32" -ErrorAction SilentlyContinue

Write-Host "4. Setting Environment Variables..."
# We assume Java is installed in C:\Program Files\Eclipse Adoptium\jdk-8.0.x (typical winget path)
# Let's find it dynamically
$javaHomes = Get-ChildItem -Path "C:\Program Files\Eclipse Adoptium" -Directory | Select-Object -ExpandProperty FullName
if ($javaHomes) {
    $javaHome = $javaHomes[0]
} else {
    $javaHome = "C:\Progra~1\Java\jdk1.8.0_xxx" # Placeholder, user might need to fix
}

[Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "User")
[Environment]::SetEnvironmentVariable("HADOOP_HOME", $hadoopHome, "User")

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notmatch "Hadoop") {
    $newPath = $currentPath + ";$hadoopHome\bin;$hadoopHome\sbin"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Host "5. Configuring Hadoop XML Files..."
$etcDir = "$hadoopHome\etc\hadoop"

# hadoop-env.cmd
$hadoopEnvPath = "$etcDir\hadoop-env.cmd"
$envContent = (Get-Content $hadoopEnvPath) -replace "set JAVA_HOME=.*", "set JAVA_HOME=$javaHome"
Set-Content -Path $hadoopEnvPath -Value $envContent

# core-site.xml
$coreSite = @"
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
"@
Set-Content -Path "$etcDir\core-site.xml" -Value $coreSite

# hdfs-site.xml
$hdfsSite = @"
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/C:/Hadoop/data/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/C:/Hadoop/data/datanode</value>
    </property>
</configuration>
"@
Set-Content -Path "$etcDir\hdfs-site.xml" -Value $hdfsSite

Write-Host "6. Formatting Namenode..."
& "$binDir\hdfs.cmd" namenode -format -force

Write-Host "Hadoop Installation Complete! Please close and reopen your terminals."
