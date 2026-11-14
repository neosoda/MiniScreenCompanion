Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptDir
WshShell.Run """C:\Users\NEO.NEO-PC\AppData\Local\Programs\Python\Python312\python.exe"" """ & ScriptDir & "\start_detached.py""", 0, False
