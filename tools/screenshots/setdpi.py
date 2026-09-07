import ctypes, sys
from ctypes import wintypes as w
u=ctypes.windll.user32
class LUID(ctypes.Structure): _fields_=[("Low",w.DWORD),("High",w.LONG)]
class SRC(ctypes.Structure): _fields_=[("adapterId",LUID),("id",w.DWORD),("modeInfoIdx",w.DWORD),("statusFlags",w.DWORD)]
class PATH(ctypes.Structure): _fields_=[("src",SRC),("tgt",ctypes.c_byte*48),("flags",w.DWORD)]
class HDR(ctypes.Structure): _fields_=[("type",ctypes.c_int),("size",w.DWORD),("adapterId",LUID),("id",w.DWORD)]
class GET(ctypes.Structure): _fields_=[("hdr",HDR),("minRel",ctypes.c_int),("curRel",ctypes.c_int),("maxRel",ctypes.c_int)]
class SET(ctypes.Structure): _fields_=[("hdr",HDR),("scaleRel",ctypes.c_int)]
np,nm=w.UINT(),w.UINT()
assert u.GetDisplayConfigBufferSizes(2,ctypes.byref(np),ctypes.byref(nm))==0
paths=(PATH*np.value)(); modes=(ctypes.c_byte*64*nm.value)()
assert u.QueryDisplayConfig(2,ctypes.byref(np),paths,ctypes.byref(nm),modes,None)==0
SCALES=[100,125,150,175,200,225,250,300,350,400,450,500]
for p in paths[:np.value]:
    g=GET(); g.hdr.type=-3; g.hdr.size=ctypes.sizeof(GET); g.hdr.adapterId=p.src.adapterId; g.hdr.id=p.src.id
    print("get rc",u.DisplayConfigGetDeviceInfo(ctypes.byref(g)),"min/cur/max rel",g.minRel,g.curRel,g.maxRel)
    rec=-g.minRel  # index of recommended scale
    print("recommended",SCALES[rec],"current",SCALES[rec+g.curRel],"max",SCALES[rec+g.maxRel])
    if len(sys.argv)>1:
        target=int(sys.argv[1]); rel=SCALES.index(target)-rec
        s=SET(); s.hdr.type=-4; s.hdr.size=ctypes.sizeof(SET); s.hdr.adapterId=p.src.adapterId; s.hdr.id=p.src.id; s.scaleRel=rel
        print("set",target,"rel",rel,"rc",u.DisplayConfigSetDeviceInfo(ctypes.byref(s)))
