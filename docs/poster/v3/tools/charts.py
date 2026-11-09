"""Draw the v3 poster charts as SVG with the poster's colour tokens.

The numbers are the reported values in docs/research_status.md (Always on
ConFiQA-QA, earlier external report), the 2026-11-09 same-data replay
(Packed / State-based on ConFiQA-QA and NQ-Swap) and the Growth midterm deck
(P8S 4-state probe, E14/E16).
Nothing here runs a model; it only draws.

Usage: python3 docs/poster/v3/tools/charts.py  → writes SVG files into docs/poster/v3/.
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
FONT = "Pretendard, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif"
BG, PANEL, WHITE, MUTED, LINE = "#080b10", "#10171e", "#f2f5f5", "#a9b7c2", "#35434d"
LIME, CYAN, PINK, GRAY = "#cdff5f", "#5de5ff", "#ff7aa9", "#9aaaba"

# All charts use 4 SVG units per millimetre so that font sizes convert as pt * 1.411 units.
U = 4.0


def sgn(s: str) -> str:
    """Use the true minus sign (U+2212) in numeric labels."""
    return s.replace("-", "\u2212")


def pt(size_pt: float) -> float:
    """Convert a point size to SVG units (1 pt = 0.3528 mm)."""
    return size_pt * 0.3528 * U


def text(x, y, s, size_pt, fill=WHITE, anchor="start", weight=500, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{pt(size_pt):.1f}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{FONT}" {extra}>{s}</text>')


def svg_open(w_mm, h_mm, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_mm * U:.0f} {h_mm * U:.0f}" '
            f'width="{w_mm}mm" height="{h_mm}mm" role="img" aria-label="{label}">')


def macro_f1_bars(path: Path, w_mm=320, h_mm=87):
    """4-state Macro-F1 on P8S (E14): random → whole L13 output → selected heads."""
    bars = [
        ("무작위 추측", "균등 무작위 20,000회 평균", 0.2477, GRAY, False),
        ("L13 출력 전체", "4,096차원 · Probe", 0.6215, CYAN, False),
        ("선발 헤드 조합", "헤드 1~32개 · 헤드별 128차원 · Probe", 0.6306, LIME, True),
    ]
    W, H = w_mm * U, h_mm * U
    left, right, top, bottom = 20 * U, 4 * U, 9 * U, 22 * U
    plot_w, plot_h = W - left - right, H - top - bottom
    slot = plot_w / len(bars)
    bw = slot * 0.5
    out = [svg_open(w_mm, h_mm, "4-state Macro-F1. 무작위 추측 0.2477, L13 출력 전체 0.6215, 선발 헤드 조합 0.6306.")]
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        y = top + plot_h * (1 - v)
        dash = "" if v == 0 else f' stroke-dasharray="{1.2 * U:.1f} {1.6 * U:.1f}"'
        out.append(f'<path d="M{left:.1f} {y:.1f}H{left + plot_w:.1f}" stroke="{LINE}" stroke-width="{0.3 * U:.1f}"{dash}/>')
        out.append(text(left - 3 * U, y + pt(15) * 0.35, f"{v:.2f}", 15, MUTED, "end"))
    for i, (label, sub, v, color, hero) in enumerate(bars):
        x = left + slot * i + (slot - bw) / 2
        h = plot_h * v
        y = top + plot_h - h
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{1.5 * U:.1f}" fill="{color}"/>')
        out.append(text(x + bw / 2, y - 2.2 * U, f"{v:.4f}", 28 if hero else 24, color if hero else WHITE, "middle", 800 if hero else 600, extra='paint-order="stroke" stroke="#10171e" stroke-width="10"'))
        out.append(text(x + bw / 2, top + plot_h + 8.2 * U, label, 20, WHITE, "middle", 700 if hero else 600))
        out.append(text(x + bw / 2, top + plot_h + 15.2 * U, sub, 15, MUTED, "middle"))
    # bracket between bar 2 and bar 3 with the reported difference
    x2 = left + slot * 1 + slot / 2
    x3 = left + slot * 2 + slot / 2
    yb = top + plot_h * (1 - 0.6306) - 13 * U
    out.append(f'<path d="M{x2:.1f} {yb + 2 * U:.1f}V{yb:.1f}H{x3:.1f}V{yb + 2 * U:.1f}" fill="none" stroke="{MUTED}" stroke-width="{0.3 * U:.1f}"/>')
    out.append(text((x2 + x3) / 2, yb - 1.4 * U, "+0.0091", 15, MUTED, "middle"))
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def label_ratio_bars(path: Path, w_mm=190, h_mm=26):
    """E16: Macro-F1 by labelled-data ratio on the same 490 evaluation questions (5 repeats)."""
    bars = [("무작위", 0.25, GRAY), ("라벨 5%", 0.54, "#3fa9c0"), ("라벨 10%", 0.59, "#3fa9c0"), ("라벨 20%", 0.61, CYAN), ("라벨 약 80%", 0.63, LIME)]
    W, H = w_mm * U, h_mm * U
    top, bottom = 7 * U, 7 * U
    plot_h = H - top - bottom
    slot = W / len(bars)
    bw = slot * 0.58
    out = [svg_open(w_mm, h_mm, "라벨 비율별 Macro-F1. 무작위 0.25, 라벨 5% 0.54, 10% 0.59, 20% 0.61, 약 80% 0.63.")]
    out.append(f'<path d="M0 {top + plot_h:.1f}H{W:.1f}" stroke="{LINE}" stroke-width="{0.3 * U:.1f}"/>')
    for i, (label, v, color) in enumerate(bars):
        x = slot * i + (slot - bw) / 2
        h = plot_h * v
        y = top + plot_h - h
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{1 * U:.1f}" fill="{color}"/>')
        out.append(text(x + bw / 2, y - 1.6 * U, f"{v:.2f}", 16, WHITE, "middle", 700 if i >= 3 else 600))
        out.append(text(x + bw / 2, top + plot_h + 5.4 * U, label, 14, MUTED, "middle"))
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def always_bars(path: Path, w_mm=150, h_mm=22):
    """Always Steering on ConFiQA-QA: C− gain vs C+ damage (research_status.md §3)."""
    rows = [("틀린 문서 C−", 8.20, GRAY), ("맞는 문서 C+", -2.90, PINK)]
    W, H = w_mm * U, h_mm * U
    label_w, value_w = 36 * U, 20 * U
    lo, hi = -4.0, 9.0
    plot_w = W - label_w - value_w
    row_h = (H - 5 * U) / len(rows)

    def sx(v):
        return label_w + (v - lo) / (hi - lo) * plot_w

    out = [svg_open(w_mm, h_mm, "Always Steering ConFiQA-QA 변화량: 틀린 문서 C− +8.20%p, 맞는 문서 C+ −2.90%p.")]
    for t in (-4, 0, 4, 8):
        x = sx(t)
        strong = t == 0
        out.append(f'<path d="M{x:.1f} 0V{H - 5 * U:.1f}" stroke="{MUTED if strong else LINE}" stroke-width="{(0.5 if strong else 0.3) * U:.1f}"/>')
        out.append(text(x, H - 0.6 * U, sgn(f"{t:+d}") if t else "0", 14, MUTED, "middle"))
    for r, (label, val, color) in enumerate(rows):
        cy = row_h * r + row_h / 2
        out.append(text(0, cy + pt(16) * 0.35, label, 16, WHITE, "start", 600))
        xa, xb = sorted((sx(0), sx(val)))
        out.append(f'<rect x="{xa:.1f}" y="{cy - 2.6 * U:.1f}" width="{xb - xa:.1f}" height="{5.2 * U:.1f}" rx="{0.8 * U:.1f}" fill="{color}"/>')
        out.append(text(W, cy + pt(20) * 0.35, sgn(f"{val:+.2f}"), 20, color, "end", 700))
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def replay_em_panels(path: Path, w_mm=536, h_mm=66.5):
    """Same-data replay (2026-11-09): change vs the common no-intervention base, ConFiQA-QA and NQ-Swap.

    Rows are methods; each method block has one bar per dataset. Values are
    delta_vs_common_base_pp from EM_AND_PRESERVATION.csv (scope full_fixed_test).
    """
    rows = [
        ("Packed", "문서 본 답·안 본 답 비교 · 기준값은 대상 dev로 정함 · 3회 평균", CYAN),
        ("Packed · 판독 없이", "State-based와 같은 후보에서 판독 보호만 뺌", GRAY),
        ("State-based", "L13 판독이 K−C+면 문서 쪽으로 개입 · 판독기는 P8S로 학습", LIME),
    ]
    datasets = ("ConFiQA-QA", "NQ-Swap")
    # (ConFiQA-QA, NQ-Swap) per row, per panel
    panels = [
        ("전체 정답률 변화", "%p · 같은 기준선(개입 없음) 대비",
         [(1.77, 3.93), (1.65, 4.00), (1.90, 4.10)], (0, 4.8), [0, 2, 4]),
        ("틀린 문서(C−)에서", "%p · 클수록 틀린 문서에 덜 흔들림",
         [(7.83, 10.83), (6.90, 9.70), (6.90, 9.40)], (0, 11.6), [0, 5, 10]),
        ("맞는 문서(C+)에서", "%p · 0 아래는 맞히던 답의 손상",
         [(-4.30, -2.97), (-3.60, -1.70), (-3.10, -1.20)], (-4.8, 0.4), [-4, -2, 0]),
    ]
    W, H = w_mm * U, h_mm * U
    name_w, label_w, gap = 122 * U, 156 * U, 10 * U
    value_w = 20 * U
    panel_w = (W - label_w - gap * (len(panels) - 1)) / len(panels)
    plot_w = panel_w - value_w
    top, bottom = 16 * U, 8.5 * U
    sub_h, block_gap = 6 * U, 3 * U
    block_h = sub_h * len(datasets)

    def block_top(r):
        return top + r * (block_h + block_gap)

    def sub_cy(r, d):
        return block_top(r) + sub_h * d + sub_h / 2

    plot_bottom = block_top(len(rows) - 1) + block_h
    out = [svg_open(w_mm, h_mm, "같은 데이터 재평가, 개입 없음 대비 변화(%p). 전체: Packed +1.77/+3.93, 판독 없는 Packed +1.65/+4.00, "
                    "State-based +1.90/+4.10. 틀린 문서 C−: +7.83/+10.83, +6.90/+9.70, +6.90/+9.40. "
                    "맞는 문서 C+: −4.30/−2.97, −3.60/−1.70, −3.10/−1.20. 앞은 ConFiQA-QA, 뒤는 NQ-Swap.")]
    for r, (name, cond, color) in enumerate(rows):
        cy = block_top(r) + block_h / 2
        out.append(text(0, cy - 0.6 * U, name, 22, color, "start", 700))
        out.append(text(0, cy + 5.2 * U, cond, 14, MUTED, "start"))
        for d, ds in enumerate(datasets):
            out.append(text(label_w - 3 * U, sub_cy(r, d) + pt(14) * 0.35, ds, 14, MUTED, "end"))
    for p, (title, sub, vals, (lo, hi), ticks) in enumerate(panels):
        x0 = label_w + p * (panel_w + gap)

        def sx(v, x0=x0, lo=lo, hi=hi):
            return x0 + (v - lo) / (hi - lo) * plot_w

        out.append(text(x0, 5.2 * U, title, 19, WHITE, "start", 700))
        out.append(text(x0, 11.2 * U, sub, 14, MUTED, "start"))
        for t in ticks:
            x = sx(t)
            strong = t == 0
            out.append(f'<path d="M{x:.1f} {top - 1.5 * U:.1f}V{plot_bottom:.1f}" stroke="{MUTED if strong else LINE}" stroke-width="{(0.5 if strong else 0.3) * U:.1f}"/>')
            out.append(text(x, plot_bottom + 6.2 * U, sgn(f"{t:+d}") if t else "0", 15, MUTED, "middle"))
        for r, pair in enumerate(vals):
            color = rows[r][2]
            for d, val in enumerate(pair):
                cy = sub_cy(r, d)
                bar_color = PINK if val < 0 else color
                xa, xb = sorted((sx(0), sx(val)))
                out.append(f'<rect x="{xa:.1f}" y="{cy - 2.1 * U:.1f}" width="{max(xb - xa, 0.6 * U):.1f}" height="{4.2 * U:.1f}" rx="{0.6 * U:.1f}" fill="{bar_color}"/>')
                vx = x0 + panel_w - 0.5 * U
                vcolor = PINK if val < 0 else color
                out.append(text(vx, cy + pt(17) * 0.35, sgn(f"{val:+.2f}"), 17, vcolor, "end", 700))
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    macro_f1_bars(OUT / "chart-macro-f1.svg")
    label_ratio_bars(OUT / "chart-label-ratio.svg")
    always_bars(OUT / "chart-always.svg")
    replay_em_panels(OUT / "chart-replay-em.svg")
    print("wrote chart-macro-f1.svg chart-label-ratio.svg chart-always.svg chart-replay-em.svg in", OUT)
