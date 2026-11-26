import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle, FancyArrowPatch
import sys

for f in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in f or "NotoSansCJK-Medium" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "DejaVu Sans"]

W, L, EAVE, RIDGE, BAY = 50, 100, 5, 11.75, 5
# layout (y = 0 entrance end, y = L stage end)
BACK = 1.5
ST_W, ST_D, ST_H = 24.4, 9.76, 1.0
ST_Y1 = L - BACK; ST_Y0 = ST_Y1 - ST_D
ST_X0 = (W - ST_W) / 2; ST_X1 = ST_X0 + ST_W
FRONT_GAP = 5
SEAT_W, ROW = 0.55, 1.0
ROWS = 68
SEAT_Y1 = ST_Y0 - FRONT_GAP; SEAT_Y0 = SEAT_Y1 - ROWS * ROW
AISLE = 2.5
blocks_seats = [22, 30, 22]
bw = [n * SEAT_W for n in blocks_seats]
side = (W - sum(bw) - 2 * AISLE) / 2
xs = []; x = side
for i, b in enumerate(bw):
    xs.append((x, x + b)); x += b + (AISLE if i < 2 else 0)
seats = sum(blocks_seats) * ROWS
REAR = SEAT_Y0

C_FRAME, C_ROOF, C_SEAT, C_STAGE, C_AISLE, RED = "#3a3f44", "#e9eef2", "#7fb3d5", "#8d5a3b", "#f6e7b0", "#c0392b"

fig = plt.figure(figsize=(24, 16.5), dpi=100)
fig.text(0.04, 0.955, "Church Tent Layout 教会篷房布局 — 50 m × 100 m · 约 5,000 座", fontsize=30, weight="bold")
fig.text(0.04, 0.925, f"Span 50 m · Length 100 m · Area 5,000 m² · Eave {EAVE} m · Ridge {RIDGE} m · Bay {BAY} m · "
         f"Stage {ST_W} × {ST_D} × 0.4–0.8 m · 2 long aisles {AISLE} m · {seats:,} seats",
         fontsize=16, color="#555")
fig.text(0.96, 0.955, "SUZHOU GUYUN TENT CO., LTD.", fontsize=20, weight="bold", ha="right")
fig.text(0.96, 0.928, "www.gy-tent.com", fontsize=15, color="#555", ha="right")

# ---------- 3D (manual axonometric, painter's order) ----------
import numpy as np
ax = fig.add_axes([0.02, 0.10, 0.60, 0.78])
TH, PH = np.radians(32), np.radians(30)
def P(x, y, z):
    X = x*np.cos(TH) + y*np.sin(TH)
    Y = (-x*np.sin(TH) + y*np.cos(TH))*np.sin(PH) + z*1.0
    return X, Y
from matplotlib.patches import Polygon
def poly(pts, fc, ec="none", a=1.0, lw=0.6, z=1):
    ax.add_patch(Polygon([P(*p) for p in pts], closed=True, fc=fc, ec=ec, alpha=a, lw=lw, zorder=z))
def line(p0, p1, c=C_FRAME, lw=0.9, ls="-", z=5, a=0.55):
    (x0,y0),(x1,y1) = P(*p0), P(*p1); ax.plot([x0,x1],[y0,y1], color=c, lw=lw, ls=ls, zorder=z, alpha=a)
def box(x0,x1,y0,y1,z0,z1,top,side,front,z=3):
    poly([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)], top, "#00000055", 1, 0.5, z)
    poly([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)], front, "#00000055", 1, 0.5, z)   # face toward entrance
    poly([(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)], side, "#00000055", 1, 0.5, z)   # left face
# far frames / walls first
poly([(0,0,0),(W,0,0),(W,L,0),(0,L,0)], "#efefef", "#888", 1, 1, 1)
poly([(0,L,0),(W,L,0),(W,L,EAVE),(W/2,L,RIDGE),(0,L,EAVE)], "#dde5ea", "none", 0.6, 0, 1)
poly([(W,0,0),(W,L,0),(W,L,EAVE),(W,0,EAVE)], "#dde5ea", "none", 0.45, 0, 1)
for (a0, a1) in [(xs[0][1], xs[1][0]), (xs[1][1], xs[2][0])]:
    poly([(a0,SEAT_Y0,0),(a1,SEAT_Y0,0),(a1,SEAT_Y1,0),(a0,SEAT_Y1,0)], C_AISLE, "none", 1, 0, 2)
# stage (far) then seat blocks from far to near
box(ST_X0, ST_X1, ST_Y0, ST_Y1, 0, ST_H*1.6, "#a86f4a", "#6e452c", C_STAGE, 3)
tx, ty = P(W/2, (ST_Y0+ST_Y1)/2, ST_H*1.6)
ax.text(tx, ty, "STAGE 舞台", ha="center", va="center", fontsize=12, weight="bold", color="white", zorder=4)
for i, (x0, x1) in enumerate(xs[::-1]):
    box(x0, x1, SEAT_Y0, SEAT_Y1, 0, 0.6, C_SEAT, "#5d8fb3", "#4f86b0", 3)
    for r in range(0, ROWS + 1, 4):
        y = SEAT_Y0 + r*ROW; line((x0,y,0.6),(x1,y,0.6), "#3f6f96", 0.4, z=3.5)
# frames
for y in np.arange(0, L + 0.01, BAY):
    line((0,y,0),(0,y,EAVE)); line((W,y,0),(W,y,EAVE))
    line((0,y,EAVE),(W/2,y,RIDGE)); line((W/2,y,RIDGE),(W,y,EAVE))
for (xx, zz) in [(0,EAVE),(W,EAVE),(W/2,RIDGE),(W/4,(EAVE+RIDGE)/2),(3*W/4,(EAVE+RIDGE)/2)]:
    line((xx,0,zz),(xx,L,zz), lw=0.8)
for y in (0, L):
    for xx in (W/4, W/2, 3*W/4):
        zt = EAVE + (RIDGE-EAVE)*(1-abs(xx-W/2)/(W/2)); line((xx,y,0),(xx,y,zt), lw=0.8, ls="--")
poly([(0,0,EAVE),(W/2,0,RIDGE),(W/2,L,RIDGE),(0,L,EAVE)], C_ROOF, "none", 0.18, 0, 6)
poly([(W,0,EAVE),(W/2,0,RIDGE),(W/2,L,RIDGE),(W,L,EAVE)], C_ROOF, "none", 0.30, 0, 6)
ex, ey = P(W/2-2, -9, 0)
ax.text(ex, ey, "Entrance 入口", ha="center", va="top", fontsize=13, color=RED, weight="bold")
for xx in (W/2-6, W/2+6):
    (a,b),(c,d) = P(xx,-5,0), P(xx,-0.5,0)
    ax.annotate("", xy=(c,d), xytext=(a,b), arrowprops=dict(arrowstyle="->", color=RED, lw=2), zorder=7)
lx, ly = P(W+9, L*0.45, 0)
ax.text(lx, ly, "Length 100 m", color=RED, fontsize=13, weight="bold", rotation=np.degrees(np.arctan2(np.cos(TH)*np.sin(PH), np.sin(TH))), ha="left", va="top")
wx, wy = P(W*0.78, -3, 0)
ax.text(wx, wy, "Span 50 m", color=RED, fontsize=13, weight="bold", rotation=np.degrees(np.arctan2(-np.sin(TH)*np.sin(PH), np.cos(TH))), ha="left", va="top")
sx, sy = P(W/2, -1, 0)
ax.autoscale_view(); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.05, 0.86, "3D 示意 / 3D View", fontsize=17, weight="bold")

# ---------- Plan ----------
px = fig.add_axes([0.63, 0.09, 0.34, 0.80])
px.set_aspect("equal")
px.add_patch(Rectangle((0,0), W, L, fc="#fafafa", ec="#222", lw=2))
for (x0, x1), n in zip(xs, blocks_seats):
    px.add_patch(Rectangle((x0, SEAT_Y0), x1-x0, SEAT_Y1-SEAT_Y0, fc=C_SEAT, ec="#4a7aa0", lw=1))
    for r in range(0, ROWS + 1, 2):
        y = SEAT_Y0 + r * ROW
        px.plot([x0, x1], [y, y], color="#5d8fb3", lw=0.3)
    px.text((x0+x1)/2, (SEAT_Y0+SEAT_Y1)/2, f"{n} × {ROWS}\n= {n*ROWS:,}", ha="center", va="center", fontsize=12, weight="bold", color="#1f4e70")
for (a0, a1) in [(xs[0][1], xs[1][0]), (xs[1][1], xs[2][0])]:
    px.add_patch(Rectangle((a0, SEAT_Y0), a1-a0, SEAT_Y1-SEAT_Y0, fc=C_AISLE, ec="none"))
    px.text((a0+a1)/2, SEAT_Y0 + 20, f"Aisle 过道 {AISLE} m", rotation=90, ha="center", va="center", fontsize=10, color="#7a5b00")
px.add_patch(Rectangle((ST_X0, ST_Y0), ST_W, ST_D, fc=C_STAGE, ec="#5b3a26", lw=1.5))
px.text(W/2, (ST_Y0+ST_Y1)/2, f"STAGE 舞台\n{ST_W} × {ST_D} m\nH 0.4–0.8 m", ha="center", va="center", fontsize=12, weight="bold", color="white")
px.text(W/2, SEAT_Y1 + FRONT_GAP/2, f"Front space 前区 {FRONT_GAP} m", ha="center", va="center", fontsize=10, color="#555")
px.text(W/2, REAR/2, f"Entrance / foyer / sound desk\n入口·门厅·调音台  {REAR:.1f} m", ha="center", va="center", fontsize=10, color="#555")
px.annotate("", xy=(W/2 - 6, -0.5), xytext=(W/2 - 6, -6), arrowprops=dict(arrowstyle="->", color=RED, lw=2))
px.annotate("", xy=(W/2 + 6, -0.5), xytext=(W/2 + 6, -6), arrowprops=dict(arrowstyle="->", color=RED, lw=2))
px.text(W/2, -8.5, "Entrance 入口", ha="center", fontsize=11, color=RED, weight="bold")
def dim(x0, y0, x1, y1, txt, off, vertical=False):
    px.annotate("", xy=(x0, y0), xytext=(x1, y1), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.1))
    if vertical:
        px.text(x0 + off, (y0+y1)/2, txt, rotation=90, ha="center", va="center", fontsize=10, color=RED)
    else:
        px.text((x0+x1)/2, y0 + off, txt, ha="center", va="center", fontsize=10, color=RED)
dim(0, L + 3, W, L + 3, "Span 跨度 50 m", 1.6)
dim(-3, 0, -3, L, "Length 长度 100 m (20 bays × 5 m)", -1.8, True)
dim(W + 3, SEAT_Y0, W + 3, SEAT_Y1, f"Seating 座位区 {ROWS} m ({ROWS} rows × {ROW} m)", 1.8, True)
dim(W + 3, ST_Y0, W + 3, ST_Y1, f"{ST_D} m", 1.8, True)
dim(0, SEAT_Y0 - 2, xs[0][0], SEAT_Y0 - 2, "", 0); px.text(xs[0][0]+0.8, SEAT_Y0 - 2, f"墙边通道 {side:.2f} m", fontsize=10, color=RED, va="center")
px.set_xlim(-8, W + 8); px.set_ylim(-11, L + 7)
px.axis("off")
px.set_title("平面图 / Floor Plan", fontsize=17, weight="bold", loc="left")

# ---------- notes ----------
fig.text(0.04, 0.075,
    f"座位 Seating: 剧院式排椅，椅宽 {SEAT_W} m，排距 {ROW} m；三区 {blocks_seats[0]} + {blocks_seats[1]} + {blocks_seats[2]} = {sum(blocks_seats)} 座/排 × {ROWS} 排 = {seats:,} 座。"
    f"两侧墙边通道 {side:.2f} m，2 条纵向长过道各 {AISLE} m。",
    fontsize=14)
fig.text(0.04, 0.05,
    f"舞台 Stage: {ST_W} × {ST_D} m ≈ {ST_W*ST_D:.0f} m²，高 0.4–0.8 m 可调 / height 0.4–0.8 m adjustable（台板 1.22 × 2.44 m：宽 10 块、深 4 块），舞台后预留 {BACK} m。",
    fontsize=14)
fig.text(0.04, 0.025, "示意图，尺寸与座位数以最终设计和当地消防要求为准 / Schematic only — final layout subject to detailed design and local fire regulations.",
    fontsize=12, color="#666")
out = sys.argv[1]
fig.savefig(out, dpi=100)
print("seats", seats, "side", round(side, 2), "rear", round(REAR, 2), "seatY", round(SEAT_Y0, 2), round(SEAT_Y1, 2))
