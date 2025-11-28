Set WshShell = CreateObject("WScript.Shell") 
' Sondaki 0 rakamı "Pencereyi Gizle" demektir.
WshShell.Run chr(34) & "Baslat.bat" & chr(34), 0
Set WshShell = Nothing