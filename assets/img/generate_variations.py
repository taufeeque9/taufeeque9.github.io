"""Generate 10 SVG favicon variations with different seeds/architectures."""

import random

# ─── Shared colors ────────────────────────────────────────────────────────────
COLOR_ENDPOINT = "#6366F1"
COLOR_FEATURE = "#F43F5E"
COLOR_MID_COOL = "#9B6AB8"
COLOR_MID_WARM = "#B56E9A"

SIZE = 64

# ─── 10 variations: (seed, layers, jitter, padding, feature_index, edge_min, edge_max, r_io, r_feat, r_default) ───
VARIATIONS = [
    {"seed": 99,  "layers": [1, 3, 5, 3, 1], "jitter": 3, "padding": 7, "feat_idx": 2},
    {"seed": 42,  "layers": [1, 3, 5, 3, 1], "jitter": 4, "padding": 7, "feat_idx": 2},
    {"seed": 7,   "layers": [1, 3, 5, 3, 1], "jitter": 3, "padding": 8, "feat_idx": 1},
    {"seed": 55,  "layers": [1, 3, 5, 3, 1], "jitter": 5, "padding": 7, "feat_idx": 3},
    {"seed": 21,  "layers": [1, 3, 5, 3, 1], "jitter": 3, "padding": 6, "feat_idx": 2},
    {"seed": 77,  "layers": [1, 3, 5, 3, 1], "jitter": 4, "padding": 8, "feat_idx": 0},
    {"seed": 33,  "layers": [1, 3, 5, 3, 1], "jitter": 2, "padding": 7, "feat_idx": 4},
    {"seed": 13,  "layers": [1, 3, 5, 3, 1], "jitter": 4, "padding": 6, "feat_idx": 2},
    {"seed": 88,  "layers": [1, 3, 5, 3, 1], "jitter": 3, "padding": 7, "feat_idx": 1},
    {"seed": 64,  "layers": [1, 3, 5, 3, 1], "jitter": 5, "padding": 7, "feat_idx": 2},
]

EDGE_WIDTH_MIN = 0.6
EDGE_WIDTH_MAX = 2.2
RADIUS_IO = 4.5
RADIUS_FEATURE = 4.5
RADIUS_DEFAULT = 3.0


def lerp_color(hex1, hex2, t):
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def generate(var, output_path):
    random.seed(var["seed"])
    layers = var["layers"]
    jitter = var["jitter"]
    padding = var["padding"]
    feat_layer = len(layers) // 2
    feat_idx = var["feat_idx"]
    n_layers = len(layers)
    max_layer_size = max(layers)

    def node_color(li, ni):
        if li == 0 or li == n_layers - 1:
            return COLOR_ENDPOINT
        if li == feat_layer and ni == feat_idx:
            return COLOR_FEATURE
        dist = abs(li - feat_layer) / feat_layer
        return lerp_color(COLOR_MID_WARM, COLOR_MID_COOL, dist)

    def node_radius(li, ni):
        if li == 0 or li == n_layers - 1:
            return RADIUS_IO
        if li == feat_layer and ni == feat_idx:
            return RADIUS_FEATURE
        return RADIUS_DEFAULT + random.uniform(-0.5, 0.5)

    def is_feature(li, ni):
        return li == feat_layer and ni == feat_idx

    # Place nodes
    x_positions = [
        padding + i * (SIZE - 2 * padding) / (n_layers - 1) for i in range(n_layers)
    ]

    nodes = []
    for li, count in enumerate(layers):
        for ni in range(count):
            x = x_positions[li]
            if count == 1:
                y = SIZE / 2
            else:
                span = (SIZE - 2 * padding) * (count / max_layer_size)
                y_start = (SIZE - span) / 2
                y = y_start + ni * span / (count - 1)

            jit = jitter if (li != 0 and li != n_layers - 1) else 0
            x += random.uniform(-jit, jit)
            y += random.uniform(-jit, jit)

            r = node_radius(li, ni)
            x = max(r + 1, min(SIZE - r - 1, x))
            y = max(r + 1, min(SIZE - r - 1, y))

            nodes.append({
                "x": round(x, 1), "y": round(y, 1),
                "layer": li, "index": ni,
                "color": node_color(li, ni),
                "radius": round(node_radius(li, ni), 1),
            })

    def get_node(li, ni):
        for n in nodes:
            if n["layer"] == li and n["index"] == ni:
                return n

    # Build edges
    edges = []
    for li in range(n_layers - 1):
        for ni in range(layers[li]):
            for nj in range(layers[li + 1]):
                src, dst = get_node(li, ni), get_node(li + 1, nj)
                edges.append({
                    "src": src, "dst": dst,
                    "width": round(random.uniform(EDGE_WIDTH_MIN, EDGE_WIDTH_MAX), 1),
                    "has_feature": is_feature(li, ni) or is_feature(li + 1, nj),
                })

    # Generate SVG
    grad_defs, grad_refs = [], {}
    for i, e in enumerate(edges):
        if e["has_feature"]:
            gid = f"g{i}"
            s, d = e["src"], e["dst"]
            grad_defs.append(
                f'    <linearGradient id="{gid}" x1="{s["x"]}" y1="{s["y"]}" '
                f'x2="{d["x"]}" y2="{d["y"]}" gradientUnits="userSpaceOnUse">\n'
                f'      <stop offset="0%" stop-color="{s["color"]}"/>'
                f'<stop offset="100%" stop-color="{d["color"]}"/>\n'
                f'    </linearGradient>'
            )
            grad_refs[i] = gid

    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">']
    if grad_defs:
        lines.append("  <defs>")
        lines.extend(grad_defs)
        lines.append("  </defs>")

    for i, e in enumerate(edges):
        s, d = e["src"], e["dst"]
        stroke = f'url(#{grad_refs[i]})' if i in grad_refs else s["color"]
        lines.append(
            f'  <line x1="{s["x"]}" y1="{s["y"]}" x2="{d["x"]}" y2="{d["y"]}" '
            f'stroke="{stroke}" stroke-width="{e["width"]}" stroke-linecap="round"/>'
        )

    for n in nodes:
        lines.append(
            f'  <circle cx="{n["x"]}" cy="{n["y"]}" r="{n["radius"]}" fill="{n["color"]}"/>'
        )

    lines.append("</svg>")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"  {output_path}: layers={layers} seed={var['seed']} jitter={jitter} feat@{feat_layer}[{feat_idx}]")


# ─── Generate all ─────────────────────────────────────────────────────────────
print("Generating 10 variations...")
for i, var in enumerate(VARIATIONS):
    generate(var, f"favicon-v{i + 1}.svg")
print("Done!")
