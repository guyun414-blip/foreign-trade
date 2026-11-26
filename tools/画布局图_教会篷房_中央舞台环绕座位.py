# 教会篷房：中央舞台 + 四周环绕座位 布局草图（平面图 + 横剖面）
# 用法: python3 画布局图_教会篷房_中央舞台环绕座位.py <输出png>
import sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Polygon
for f in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in f or "NotoSansCJK-Medium" in f or "NotoSansCJK-Bold" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK SC", "DejaVu Sans"]

W, L, EAVE, RIDGE, BAY = 50, 100, 5.0, 11.7, 5
CX, CY = W/2, L/2
ST = 12.2; ST_H = 1.2                    # 舞台 12.2 x 12.2（台板 1.22x2.44：10x5 块）
TR = ST + 2.0; TR_H = 7.0                # 桁架 14.2 x 14.2，高 7 m
GAP = 3.0                                # 舞台四周通道
SEAT_W, ROW = 0.55, 1.0
WALL = 2.2; CROSS = 2.5; AISLE = 2.0
inner = ST/2 + GAP                       # 9.1
# 两端座区（面向舞台）
sec_n = 18; secs = 4
sx = []; x = WALL
for i in range(secs):
    sx.append((x, x + sec_n*SEAT_W)); x += sec_n*SEAT_W + AISLE
R1 = R2 = 15
blocks = []   # (x0,x1,y0,y1, orient 'h'/'v', seats)
for sgn in (-1, 1):
    yA = CY + sgn*inner
    y_r1 = sorted([yA, yA + sgn*R1*ROW]); y_c = sorted([yA + sgn*R1*ROW, yA + sgn*(R1*ROW+CROSS)])
    y_r2 = sorted([yA + sgn*(R1*ROW+CROSS), yA + sgn*(R1*ROW+CROSS+R2*ROW)])
    for (x0, x1) in sx:
        blocks.append((x0, x1, *y_r1, 'h', sec_n*R1))
        blocks.append((x0, x1, *y_r2, 'h', sec_n*R2))
    if sgn == -1: CROSS_S = y_c; FOYER_S = y_r2[0]
    else: CROSS_N = y_c; FOYER_N = y_r2[1]
# 两侧座区
SIDE_ROWS = 13; side_seats = 27
sy0 = CY - side_seats*SEAT_W/2; sy1 = CY + side_seats*SEAT_W/2
for sgn in (-1, 1):
    xA = CX + sgn*inner; xs_ = sorted([xA, xA + sgn*SIDE_ROWS*ROW])
    blocks.append((xs_[0], xs_[1], sy0, sy1, 'v', side_seats*SIDE_ROWS))
# 调音台（南区横走道后，中间）
SD = (CX-4, CX+4, CROSS_S[0]-4, CROSS_S[0])
sd_loss = 2 * 5 * 4
total = sum(b[5] for b in blocks) - sd_loss
far = (CY - ST/2) - FOYER_S
roof = lambda xx: EAVE + (RIDGE-EAVE)*(1 - abs(xx-CX)/CX)

C_SEAT, C_STAGE, C_TRUSS, C_AISLE, RED, GREY = "#7fb3d5", "#8d5a3b", "#555b61", "#f6e7b0", "#c0392b", "#555"
fig = plt.figure(figsize=(24, 17), dpi=100)
fig.text(0.04, 0.955, f"Church Tent Layout 教会篷房 — Center Stage 中央舞台 · 约 {round(total,-2):,.0f} 座", fontsize=30, weight="bold")
fig.text(0.04, 0.927, f"Span {W} m · Length {L} m · Area 5,000 m² · Eave {EAVE:g} m · Ridge {RIDGE:g} m · "
         f"Stage {ST} × {ST} × {ST_H} m · Truss {TR} × {TR} × {TR_H:g} m · {total:,} seats", fontsize=16, color=GREY)
fig.text(0.96, 0.955, "SUZHOU GUYUN TENT CO., LTD.", fontsize=20, weight="bold", ha="right")
fig.text(0.96, 0.928, "www.gy-tent.com", fontsize=15, color=GREY, ha="right")

# ---------- 平面图（长度方向横放：u = y, v = x）----------
px = fig.add_axes([0.04, 0.40, 0.92, 0.48]); px.set_aspect("equal"); px.axis("off")
R = lambda x0, x1, y0, y1, **k: px.add_patch(Rectangle((y0, x0), y1-y0, x1-x0, **k))
R(0, W, 0, L, fc="#fafafa", ec="#222", lw=2.5)
for b in range(1, L//BAY): px.plot([b*BAY]*2, [0, W], color="#ddd", lw=0.6, zorder=0)
R(0, W, CROSS_S[0], CROSS_S[1], fc=C_AISLE, ec="none"); R(0, W, CROSS_N[0], CROSS_N[1], fc=C_AISLE, ec="none")
for i in range(secs-1):
    a0, a1 = sx[i][1], sx[i+1][0]
    R(a0, a1, FOYER_S, CY-inner, fc=C_AISLE, ec="none"); R(a0, a1, CY+inner, FOYER_N, fc=C_AISLE, ec="none")
for (x0, x1, y0, y1, o, n) in blocks:
    R(x0, x1, y0, y1, fc=C_SEAT, ec="#4a7fa3", lw=0.8)
    if o == 'h':
        yy = y0 + ROW
        while yy < y1 - 0.01: px.plot([yy, yy], [x0, x1], color="#5b93ba", lw=0.4); yy += ROW
    else:
        xx = x0 + ROW
        while xx < x1 - 0.01: px.plot([y0, y1], [xx, xx], color="#5b93ba", lw=0.4); xx += ROW
for (x0, x1, y0, y1, o, n) in blocks:
    if o == 'h' and x0 == sx[0][0]:
        px.text((y0+y1)/2, (x0+x1)/2, f"{sec_n}×{int(round(y1-y0))}\n={n}", ha="center", va="center", fontsize=9, color="#1f4e70", weight="bold")
    if o == 'v':
        px.text((y0+y1)/2, (x0+x1)/2, f"{side_seats}×{SIDE_ROWS}\n={n}", ha="center", va="center", fontsize=11, color="#1f4e70", weight="bold")
R(SD[0], SD[1], SD[2], SD[3], fc="#444", ec="none"); px.text((SD[2]+SD[3])/2, CX, "Sound\n调音台", color="white", ha="center", va="center", fontsize=9)
R(CX-TR/2, CX+TR/2, CY-TR/2, CY+TR/2, fc="none", ec=C_TRUSS, lw=3, ls="--")
R(CX-ST/2, CX+ST/2, CY-ST/2, CY+ST/2, fc=C_STAGE, ec="#5a3520", lw=1.5)
for dx in (-1, 1):
    for dy in (-1, 1): R(CX+dx*TR/2-0.3, CX+dx*TR/2+0.3, CY+dy*TR/2-0.3, CY+dy*TR/2+0.3, fc=C_TRUSS, ec="none")
px.text(CY, CX, f"STAGE 舞台\n{ST} × {ST} m\nH {ST_H} m\nTruss 桁架 {TR_H:g} m", ha="center", va="center", fontsize=12, weight="bold", color="white")
for yy, t in ((FOYER_S/2, "Entrance / foyer\n入口·门厅"), ((FOYER_N+L)/2, "Entrance / foyer\n入口·门厅")):
    px.text(yy, CX, t.replace(" / ", "/\n") + f"\n{FOYER_S:.1f} m", ha="center", va="center", fontsize=9, color=GREY)
for yy in (0, L):
    for xx in (CX-8, CX+8):
        px.annotate("", xy=(yy, xx), xytext=(yy + (-5 if yy == 0 else 5), xx), arrowprops=dict(arrowstyle="->", color=RED, lw=2))
for yy in ((CROSS_S[0]+CROSS_S[1])/2, CY-inner+0.75*0+ (sy0-(CY-inner))/2, CY+inner-(sy0-(CY-inner))/2, (CROSS_N[0]+CROSS_N[1])/2):
    for xx, d in ((0, -2.5), (W, 2.5)):
        px.annotate("", xy=(yy, xx+d), xytext=(yy, xx), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.8))
px.text(L/2, -5.6, "绿色箭头 = 侧面安全出口（对准横走道）/ Green = side emergency exits", ha="center", fontsize=11, color="#27ae60")
px.text(-6.5, CX, "Entrance\n入口", ha="center", va="center", fontsize=11, color=RED, weight="bold")
px.text(L+6.5, CX, "Entrance\n入口", ha="center", va="center", fontsize=11, color=RED, weight="bold")
px.annotate("", xy=(0, W+2.2), xytext=(L, W+2.2), arrowprops=dict(arrowstyle="<->", color=RED))
px.text(L/2, W+3.2, f"Length 长度 {L} m（{L//BAY} bays × {BAY} m）", ha="center", fontsize=11, color=RED)
px.annotate("", xy=(L+1.5, 0), xytext=(L+1.5, W), arrowprops=dict(arrowstyle="<->", color=RED))
px.text(L+2.6, W*0.8, f"Span {W} m", rotation=90, ha="center", va="center", fontsize=11, color=RED)
px.annotate("", xy=(FOYER_S, -1.3), xytext=(CY-ST/2, -1.3), arrowprops=dict(arrowstyle="<->", color=GREY))
px.text((FOYER_S+CY-ST/2)/2, -2.6, f"最远排到舞台 {far:.1f} m", ha="center", fontsize=10, color=GREY)
px.set_xlim(-9, L+9); px.set_ylim(-7, W+5)
px.set_title("平面图 / Floor Plan", fontsize=17, weight="bold", loc="left")

# ---------- 横剖面（过舞台中心，跨度方向）----------
sx_ = fig.add_axes([0.04, 0.07, 0.50, 0.29]); sx_.set_aspect("equal"); sx_.axis("off")
sx_.plot([-2, W+2], [0, 0], color="#333", lw=1.5)
sx_.plot([0, 0, CX, W, W], [0, EAVE, RIDGE, EAVE, 0], color="#222", lw=2.2)
sx_.add_patch(Rectangle((CX-ST/2, 0), ST, ST_H, fc=C_STAGE, ec="#5a3520"))
for xx in (CX-TR/2, CX+TR/2): sx_.add_patch(Rectangle((xx-0.2, 0), 0.4, TR_H, fc=C_TRUSS))
sx_.add_patch(Rectangle((CX-TR/2-0.2, TR_H-0.4), TR+0.4, 0.4, fc=C_TRUSS))
for sgn in (-1, 1):
    for r in range(SIDE_ROWS):
        xx = CX + sgn*(inner + 0.5 + r)
        sx_.plot([xx, xx], [0, 0.45], color="#4a7fa3", lw=1.2); sx_.plot([xx], [1.15], "o", ms=3, color="#4a7fa3")
def vd(x, y0, y1, t, side=1):
    sx_.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", color=RED, lw=1))
    sx_.text(x + 0.6*side, (y0+y1)/2, t, color=RED, fontsize=10, va="center", ha="left" if side > 0 else "right")
vd(-0.8, 0, EAVE, f"Eave 边高 {EAVE:g} m", -1); vd(CX, ST_H, RIDGE, ""); sx_.text(CX+1.2, RIDGE-3.2, f"Ridge 顶高 {RIDGE:g} m", color=RED, fontsize=10)
vd(CX+TR/2+1.2, 0, TR_H, f"Truss 桁架 {TR_H:g} m"); vd(CX+ST/2-1.0, 0, ST_H, "", 1)
sx_.text(CX-ST/2+0.3, ST_H+0.4, f"Stage 舞台 {ST_H} m", fontsize=10, color=C_STAGE, weight="bold")
cl = roof(CX-TR/2) - TR_H
sx_.annotate("", xy=(CX-TR/2, TR_H), xytext=(CX-TR/2, roof(CX-TR/2)), arrowprops=dict(arrowstyle="<->", color="#27ae60"))
sx_.text(CX-TR/2-0.5, TR_H+cl/2, f"净空 {cl:.1f} m", color="#27ae60", fontsize=10, ha="right", va="center")
sx_.text(CX, -1.2, f"Side seats 侧区 {SIDE_ROWS} rows        Stage {ST} m        Side seats 侧区 {SIDE_ROWS} rows", ha="center", fontsize=10, color=GREY)
sx_.set_xlim(-8, W+3); sx_.set_ylim(-2, RIDGE+1.5)
sx_.set_title("横剖面 / Cross Section（过舞台中心）", fontsize=15, weight="bold", loc="left")

notes = [
 "座位 Seating：剧院式排椅，椅宽 0.55 m，排距 1.0 m",
 f"  · 两端各 4 区 × 18 座 × 30 排 = 2 × 2,160；横走道 {CROSS} m，纵走道 {AISLE} m（中间走道直通舞台）",
 f"  · 两侧各 {side_seats} 座 × {SIDE_ROWS} 排 = 2 × {side_seats*SIDE_ROWS}；调音台占 {sd_loss} 座",
 f"  · 合计 ≈ {total:,} 座；舞台四周留 {GAP:g} m 通道，墙边通道 {WALL} m",
 f"舞台 Stage：{ST} × {ST} m（台板 1.22 × 2.44 m，10 × 5 块），建议高 {ST_H} m（腿可调 1.0–1.2 m）",
 f"  · 平地座位、最远排距舞台约 {far:.0f} m：1.2 m 能让后排越过前排人头看到台面；",
 "    中央舞台四面都有前排，再高前排要仰头、台口挡视线，不建议超过 1.2 m",
 f"桁架 Truss：{TR} × {TR} m 四柱方框，高 {TR_H:g} m（台面到桁架底约 {TR_H-0.4-ST_H:.1f} m，挂灯/音响）",
 f"  · 立柱处篷顶约 {roof(CX-TR/2):.1f} m，桁架顶到篷顶净空约 {cl:.1f} m，够挂葫芦吊点",
 "  · 后排较远，建议桁架四面各挂一块 LED 屏",
]
fig.text(0.57, 0.345, "\n".join(notes), fontsize=13, va="top", linespacing=1.6)
fig.text(0.04, 0.02, "示意图，尺寸与座位数以最终设计和当地消防要求为准 / Schematic only — final layout subject to detailed design and local fire regulations.", fontsize=11, color="#777")
fig.savefig(sys.argv[1], dpi=100)
print("seats", total, "far", round(far,1), "clear", round(cl,2), "foyer", round(FOYER_S,1))
