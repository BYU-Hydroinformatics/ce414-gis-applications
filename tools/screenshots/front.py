import ctypes, sys, time
u = ctypes.windll.user32
hw = u.FindWindowW(None, sys.argv[1] if len(sys.argv) > 1 else "Lab02")
if not hw: sys.exit("not found")
# press/release Alt so Windows lets a background process change the foreground window
u.keybd_event(0x12, 0, 0, 0); u.keybd_event(0x12, 0, 2, 0)
u.SetForegroundWindow(hw); time.sleep(0.3)
print("foreground:", u.GetForegroundWindow() == hw)
