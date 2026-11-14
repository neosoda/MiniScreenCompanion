$ErrorActionPreference = 'Stop'
$cache = Join-Path $PSScriptRoot 'cpu_temperature.json'
$temporary = "$cache.tmp"
$mutex = New-Object System.Threading.Mutex($false, 'Local\TuringCompanionCpuTemperature')
if (-not $mutex.WaitOne(0)) { exit 0 }
$computer = $null
try {
    Add-Type -Path (Join-Path $PSScriptRoot 'vendor\LibreHardwareMonitor\LibreHardwareMonitorLib.dll')
    $computer = New-Object LibreHardwareMonitor.Hardware.Computer
    $computer.IsCpuEnabled = $true
    $computer.Open()
    while ($true) {
        $value = $null
        foreach ($hardware in $computer.Hardware) {
            $hardware.Update()
            $sensor = $hardware.Sensors | Where-Object {
                $_.SensorType -eq 'Temperature' -and $_.Name -match 'Core \(Tctl/Tdie\)|CPU Package'
            } | Select-Object -First 1
            if ($null -ne $sensor -and $null -ne $sensor.Value -and $sensor.Value -gt 0 -and $sensor.Value -lt 150) {
                $value = [double]$sensor.Value
                break
            }
        }
        @{ temperature_c = $value; updated_unix = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() } |
            ConvertTo-Json -Compress | Set-Content -LiteralPath $temporary -Encoding UTF8
        Move-Item -LiteralPath $temporary -Destination $cache -Force
        Start-Sleep -Seconds 5
    }
} finally {
    if ($computer) { $computer.Close() }
    $mutex.ReleaseMutex()
    $mutex.Dispose()
}
