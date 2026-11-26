import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"]=["Noto Sans CJK SC","Noto Sans CJK JP","DejaVu Sans"]
import sys
# 用法：python3 tools/画结构图_人字顶截面平面图.py <跨度> <长度> <边高> <顶高> <主型材> <输出png> [标题]
SPAN,LEN,EAVE,RIDGE=map(float,sys.argv[1:5]); PROF=sys.argv[5]; OUT=sys.argv[6]; TITLE=sys.argv[7] if len(sys.argv)>7 else "A-Frame Tent 人字顶篷房"
BAY=5.0
def g(v): return f"{v:g}"
NB=int(LEN/BAY); NF=NB+1; GP=int(SPAN/BAY)-1
RED="#c0392b"; FR="#555"; LT="#9aa"; COV="#dcecf7"
def roof(n=80):
    xs=np.linspace(-SPAN/2,SPAN/2,n); t=np.abs(xs)/(SPAN/2)
    return xs, EAVE+(RIDGE-EAVE)*(1-t)
RX,RZ=roof()
def zr(x): return np.interp(x,RX,RZ)

fig=plt.figure(figsize=(16,10.8),dpi=110)
fig.text(0.04,0.955,f"{TITLE} — {g(SPAN)} m × {g(LEN)} m",fontsize=21,weight="bold")
fig.text(0.04,0.927,f"Span {g(SPAN)} m  •  Length {g(LEN)} m  •  Area {g(SPAN*LEN)} ㎡  •  Eave {g(EAVE)} m  •  Ridge {g(RIDGE)} m  •  Clear span (no inner columns)",fontsize=10.5,color="#333")
fig.text(0.96,0.955,"SUZHOU GUYUN TENT CO., LTD.",fontsize=12,weight="bold",ha="right")
fig.text(0.96,0.93,"www.gy-tent.com",fontsize=9.5,ha="right",color="#555")
fig.text(0.25,0.905,"3D 示意 / 3D View",fontsize=10.5)

# ---------- 3D (isometric-like) ----------
ax=fig.add_axes([0.12,0.50,0.76,0.40]); ax.set_aspect("equal"); ax.axis("off")
a=np.radians(22); b=np.radians(28); sx=0.62
def P(x,y,z): return (y*np.cos(a)*sx + x*np.cos(b), z + y*np.sin(a)*sx - x*np.sin(b))
def line(pts,**kw): ax.plot(*zip(*[P(*p) for p in pts]),**kw)
def poly(pts,**kw): ax.fill(*zip(*[P(*p) for p in pts]),**kw)
# cover fills: roof strips, near side wall (x=+SPAN/2), far gable not filled
for j in range(len(RX)-1):
    poly([(RX[j],0,RZ[j]),(RX[j+1],0,RZ[j+1]),(RX[j+1],LEN,RZ[j+1]),(RX[j],LEN,RZ[j])],color=COV,alpha=0.55,lw=0)
poly([(SPAN/2,0,0),(SPAN/2,LEN,0),(SPAN/2,LEN,EAVE),(SPAN/2,0,EAVE)],color=COV,alpha=0.45,lw=0)
gx=np.r_[-SPAN/2,RX,SPAN/2]; gz=np.r_[0,RZ,0]
poly([(x,0,z) for x,z in zip(gx,gz)],color=COV,alpha=0.35,lw=0)
# far side & ground
line([(-SPAN/2,0,0),(-SPAN/2,LEN,0)],color=LT,lw=0.8)
line([(SPAN/2,0,0),(SPAN/2,LEN,0)],color=LT,lw=0.8)
# frames
for i in range(NF):
    y=i*BAY; w=1.8 if i in (0,NF-1) else 1.4
    line([(-SPAN/2,y,0),(-SPAN/2,y,EAVE)]+[(x,y,z) for x,z in zip(RX,RZ)]+[(SPAN/2,y,EAVE),(SPAN/2,y,0)],color=FR,lw=w)
# purlins along length
for x in np.linspace(-SPAN/2,SPAN/2,9):
    line([(x,0,zr(x)),(x,LEN,zr(x))],color=FR,lw=0.9 if abs(x)<SPAN/2 else 1.3)
# gable poles both ends
for y in (0,LEN):
    for k in range(1,GP+1):
        x=-SPAN/2+k*BAY; line([(x,y,0),(x,y,zr(x))],color=FR,lw=0.9)
# X braces in end bays of near side wall
for y0 in (0,LEN-BAY):
    line([(SPAN/2,y0,0),(SPAN/2,y0+BAY,EAVE)],color=FR,lw=0.6); line([(SPAN/2,y0,EAVE),(SPAN/2,y0+BAY,0)],color=FR,lw=0.6)
    line([(-SPAN/2,y0,0),(-SPAN/2,y0+BAY,EAVE)],color=LT,lw=0.5); line([(-SPAN/2,y0,EAVE),(-SPAN/2,y0+BAY,0)],color=LT,lw=0.5)

# ---------- cross section ----------
ax2=fig.add_axes([0.04,0.07,0.50,0.36]); ax2.set_aspect("equal"); ax2.axis("off")
ax2.text(-SPAN/2-2,RIDGE+3.2,f"截面图 / Cross Section — 无柱跨度 Clear span {g(SPAN)} m",fontsize=11)
ax2.fill(gx,gz,color=COV,alpha=0.6); ax2.plot(gx,gz,color="#333",lw=2)
ax2.plot([-SPAN/2-4,SPAN/2+4],[0,0],color="#999",lw=0.8)
for k in range(1,GP+1):
    x=-SPAN/2+k*BAY; ax2.plot([x,x],[0,zr(x)],ls="--",color="#555",lw=1)
for x in (-SPAN/2,SPAN/2): ax2.add_patch(plt.Rectangle((x-0.35,-0.15),0.7,0.3,color="#333"))
ax2.text(-SPAN/2+1,RIDGE+1.6,"- - Gable poles, end frames only\n      山墙中柱（仅两端）",fontsize=7.5,color="#4a6fa5",va="top")
def dim(ax,p1,p2,txt,tx,ty,ha="center",rot=0):
    ax.annotate("",xy=p2,xytext=p1,arrowprops=dict(arrowstyle="<->",color=RED,lw=0.9))
    ax.text(tx,ty,txt,color=RED,fontsize=8,ha=ha,va="center",rotation=rot)
dim(ax2,(-SPAN/2,-1.6),(SPAN/2,-1.6),f"Span 跨度 {g(SPAN)} m",0,-2.4)
dim(ax2,(-SPAN/2-0.9,0),(-SPAN/2-0.9,EAVE),f"Eave 边高\n{g(EAVE)} m",-SPAN/2-1.3,EAVE/2,ha="right")
dim(ax2,(SPAN/2+0.9,0),(SPAN/2+0.9,RIDGE),f"Ridge 顶高\n{g(RIDGE)} m",SPAN/2+1.3,RIDGE/2,ha="left")
ax2.set_xlim(-SPAN/2-6,SPAN/2+6); ax2.set_ylim(-3.5,RIDGE+4)

# ---------- plan ----------
ax3=fig.add_axes([0.62,0.05,0.34,0.42]); ax3.set_aspect("equal"); ax3.axis("off")
ax3.text(-SPAN/2,LEN+6,f"平面图 / Plan — {NF} 榀 × 2 主柱 + 2 端 × {GP} 中柱 = {NF*2+2*GP} 根立柱",fontsize=10.5)
ax3.add_patch(plt.Rectangle((-SPAN/2,0),SPAN,LEN,color=COV,alpha=0.6))
ax3.add_patch(plt.Rectangle((-SPAN/2,0),SPAN,LEN,fill=False,ec="#333",lw=1.2))
for i in range(NF):
    y=i*BAY; ax3.plot([-SPAN/2,SPAN/2],[y,y],color="#888",lw=0.7)
    for x in (-SPAN/2,SPAN/2): ax3.plot(x,y,"s",color="#333",ms=3)
for y in (0,LEN):
    for k in range(1,GP+1): ax3.plot(-SPAN/2+k*BAY,y,"s",color="#333",ms=3)
dim(ax3,(SPAN/2+2.5,0),(SPAN/2+2.5,LEN),f"Length 长度 {g(LEN)} m\n{NB} bays × 5 m",SPAN/2+3.5,LEN/2,ha="left")
dim(ax3,(-SPAN/2,-3),(SPAN/2,-3),f"Span 跨度 {g(SPAN)} m",0,-4.8)
ax3.set_xlim(-SPAN/2-3,SPAN/2+22); ax3.set_ylim(-7,LEN+9)

fig.text(0.04,0.03,f"Frame: 6061-T6 aluminum alloy  |  Main profile {PROF}  |  Roof: 850 g/㎡ white PVC  |  Sidewalls: 650 g/㎡ white PVC  |  Bay distance 开间 5 m",fontsize=8,color="#555")
fig.text(0.04,0.013,"示意图，尺寸与型材规格以最终工程设计为准 / Schematic only — final dimensions and profiles subject to engineering design.",fontsize=8,color="#555")
fig.savefig(OUT,facecolor="white")
print("ok")
