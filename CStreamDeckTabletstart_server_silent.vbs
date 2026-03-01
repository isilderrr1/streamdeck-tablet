Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """" & CreateObject("WScript.Shell").ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Microsoft\WindowsApps\pythonw.exe"" ""C:\StreamDeckTablet\server.py""", 0, False
