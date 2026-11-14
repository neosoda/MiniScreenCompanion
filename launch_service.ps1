$pythonw = "C:\Users\NEO.NEO-PC\AppData\Local\Programs\Python\Python312\pythonw.exe"
$script = Join-Path $PSScriptRoot "run.py"
$dir = $PSScriptRoot

$cmd = "`"$pythonw`" `"$script`""
$res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = $cmd
    CurrentDirectory = $dir
}

Write-Host "Spawned ProcessId: $($res.ProcessId) (Return: $($res.ReturnValue))"
