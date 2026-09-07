# movewin.py TITLE_PREFIX [x y] -- move the first visible window whose title starts with TITLE_PREFIX to x,y (default 200,120)
import sys, ctypes, ctypes.wintypes as w
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u=ctypes.windll.user32
pre=sys.argv[1]; x=int(sys.argv[2]) if len(sys.argv)>2 else 200; y=int(sys.argv[3]) if len(sys.argv)>3 else 120
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h,l):
    if u.IsWindowVisible(h):
        n=ctypes.create_unicode_buffer(256); u.GetWindowTextW(h,n,256)
        r=w.RECT(); u.GetWindowRect(h,ctypes.byref(r))
        c=ctypes.create_unicode_buffer(256); u.GetClassNameW(h,c,256)
        hit = (n.value=='' and c.value.startswith('HwndWrapper[ArcGISPro') and r.right-r.left>100) if pre=='-' else n.value.startswith(pre)
        if hit:
            print(n.value,(r.left,r.top,r.right,r.bottom)); u.SetWindowPos(h,0,x,y,0,0,0x0001|0x0004)
            u.GetWindowRect(h,ctypes.byref(r)); print('moved to',(r.left,r.top,r.right,r.bottom))
    return True
u.EnumWindows(cb,0)
