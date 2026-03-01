#Requires AutoHotkey v2.0
#SingleInstance Force

; AZIONI:
; terminal_main  -> Terminale su Monitor 1 (principale)
; vscode_mon2    -> VS Code su Monitor 2 (verticale)
; youtube_mon3   -> YouTube su Monitor 3 (monitor 15")
; discord_mon2   -> Discord su Monitor 2 (verticale)

action := (A_Args.Length >= 1) ? A_Args[1] : ""

if (action = "terminal_main") {
    OpenTerminalOnMonitor(1)
} else if (action = "vscode_mon2") {
    OpenVSCodeOnMonitor(2)
} else if (action = "youtube_mon3") {
    OpenChromeUrlOnMonitor("https://www.youtube.com", 3)
} else if (action = "discord_mon2") {
    OpenDiscordOnMonitor(2)
} else {
    MsgBox "Azione non valida: " action
}

OpenTerminalOnMonitor(mon) {
    Run "wt.exe"
    hwnd := WaitForWindow("ahk_exe WindowsTerminal.exe", 6000)
    if hwnd
        MoveToMonitor(hwnd, mon, true)
}

OpenVSCodeOnMonitor(mon) {
    Run "code"
    hwnd := WaitForWindow("ahk_exe Code.exe", 8000)
    if hwnd
        MoveToMonitor(hwnd, mon, true)
}

OpenChromeUrlOnMonitor(url, mon) {
    Run 'chrome.exe --new-window "' url '"'
    hwnd := WaitForWindow("ahk_exe chrome.exe", 8000)
    if hwnd
        MoveToMonitor(hwnd, mon, true)
}

OpenDiscordOnMonitor(mon) {
    ; Avvio
    try {
        Run "Discord.exe"
    } catch {
        try Run "discord://"
    }

    ; 1) aspetta UNA finestra Discord (anche splash)
    hwnd := WaitForWindow("ahk_exe Discord.exe", 20000)
    if !hwnd
        hwnd := WaitForWindow("Discord", 20000)
    if !hwnd
        return

    ; 2) primo move senza maximize
    SafeMove(hwnd, mon, false)

    ; 3) Discord/Electron spesso ricrea la finestra: aspetta e ri-trova
    Sleep 1500
    hwnd2 := WinExist("ahk_exe Discord.exe")
    if !hwnd2
        hwnd2 := WinExist("Discord")

    ; se la finestra è cambiata, usa la nuova
    if hwnd2
        hwnd := hwnd2

    ; 4) secondo move + maximize
    SafeMove(hwnd, mon, true)
}

SafeMove(hwnd, mon, maximize := true) {
    ; evita crash se Discord cambia finestra
    if !hwnd
        return
    if !WinExist("ahk_id " hwnd)
        return
    try MoveToMonitor(hwnd, mon, maximize)
}


MoveToMonitor(hwnd, mon, maximize := true) {
    if !hwnd
        return

    ; Se la finestra non esiste più, esci senza errore
    if !WinExist("ahk_id " hwnd)
        return

    monitorCount := MonitorGetCount()
    if (mon < 1 || mon > monitorCount)
        mon := 1

    MonitorGetWorkArea(mon, &L, &T, &R, &B)

    try WinRestore hwnd
    W := R - L, H := B - T

    ; WinMove può fallire se la finestra cambia nel frattempo
    try WinMove L, T, W, H, hwnd

    if maximize
        try WinMaximize hwnd
}


WaitForWindow(winTitleOrAhk, timeoutMs := 6000) {
    start := A_TickCount
    while (A_TickCount - start < timeoutMs) {
        if WinExist(winTitleOrAhk)
            return WinGetID(winTitleOrAhk)
        Sleep 120
    }
    return 0
}


