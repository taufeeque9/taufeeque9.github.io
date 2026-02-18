"""Generate an SVG favicon of a neural network with a highlighted feature node."""

import random

# ─── Config ───────────────────────────────────────────────────────────────────
SEED = 42
SIZE = 64
PADDING = 7
LAYERS = [1, 3, 5, 3, 1]
JITTER = 0  # no jitter — clean symmetric layout

# Colors
COLOR_ENDPOINT = "#6366F1"  # indigo (input/output)
COLOR_FEATURE = "#F43F5E"  # rose (highlighted node)
# Intermediate colors: blend from indigo toward rose
COLOR_MID_COOL = "#9B6AB8"  # purple, closer to indigo
COLOR_MID_WARM = "#B56E9A"  # mauve, closer to rose

# Node sizing
RADIUS_IO = 4.5  # input/output nodes
RADIUS_FEATURE = 4.5  # the highlighted feature node
RADIUS_DEFAULT = 3.0  # other hidden nodes

# Edge width range
EDGE_WIDTH_MIN = 0.6
EDGE_WIDTH_MAX = 2.1

# Which node in the widest layer is the "feature" (0-indexed)
FEATURE_LAYER = len(LAYERS) // 2  # middle layer
FEATURE_INDEX = 2  # middle node in the middle layer

# ─── Helpers ──────────────────────────────────────────────────────────────────
random.seed(SEED)


def lerp_color(hex1: str, hex2: str, t: float) -> str:
    """Linearly interpolate between two hex colors."""
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def node_color(layer_idx: int, node_idx: int) -> str:
    """Color based on distance from the feature layer."""
    n_layers = len(LAYERS)
    if layer_idx == 0 or layer_idx == n_layers - 1:
        return COLOR_ENDPOINT
    if layer_idx == FEATURE_LAYER and node_idx == FEATURE_INDEX:
        return COLOR_FEATURE

    # How close is this layer to the feature layer? 0 = same, 1 = endpoint
    dist = abs(layer_idx - FEATURE_LAYER) / FEATURE_LAYER
    # Blend: close to feature → warm (rose-leaning), far → cool (indigo-leaning)
    return lerp_color(COLOR_MID_WARM, COLOR_MID_COOL, dist)


def node_radius(layer_idx: int, node_idx: int) -> float:
    """Radius based on node role."""
    n_layers = len(LAYERS)
    if layer_idx == 0 or layer_idx == n_layers - 1:
        return RADIUS_IO
    if layer_idx == FEATURE_LAYER and node_idx == FEATURE_INDEX:
        return RADIUS_FEATURE
    return RADIUS_DEFAULT + random.uniform(-0.5, 0.5)


def random_edge_width() -> float:
    return round(random.uniform(EDGE_WIDTH_MIN, EDGE_WIDTH_MAX), 1)


def is_feature(layer_idx: int, node_idx: int) -> bool:
    return layer_idx == FEATURE_LAYER and node_idx == FEATURE_INDEX


# ─── Place nodes ──────────────────────────────────────────────────────────────
n_layers = len(LAYERS)
max_layer_size = max(LAYERS)

# x positions: evenly spaced with padding
x_positions = [PADDING + i * (SIZE - 2 * PADDING) / (n_layers - 1) for i in range(n_layers)]

nodes = []  # list of (x, y, layer_idx, node_idx, color, radius)
for li, count in enumerate(LAYERS):
    for ni in range(count):
        x = x_positions[li]
        # Vertical spread proportional to layer size
        if count == 1:
            y = SIZE / 2
        else:
            span = (SIZE - 2 * PADDING) * (count / max_layer_size)
            y_start = (SIZE - span) / 2
            y = y_start + ni * span / (count - 1)

        # Add jitter (less for I/O nodes)
        jit = JITTER if (li != 0 and li != n_layers - 1) else 0
        x += random.uniform(-jit, jit)
        y += random.uniform(-jit, jit)

        # Clamp to stay inside viewBox
        r = node_radius(li, ni)
        x = max(r + 1, min(SIZE - r - 1, x))
        y = max(r + 1, min(SIZE - r - 1, y))

        nodes.append(
            {
                "x": round(x, 1),
                "y": round(y, 1),
                "layer": li,
                "index": ni,
                "color": node_color(li, ni),
                "radius": round(node_radius(li, ni), 1),
            }
        )


def get_node(layer_idx, node_idx):
    for n in nodes:
        if n["layer"] == layer_idx and n["index"] == node_idx:
            return n
    return None


# ─── Build edges ──────────────────────────────────────────────────────────────
edges = []
for li in range(n_layers - 1):
    for ni in range(LAYERS[li]):
        for nj in range(LAYERS[li + 1]):
            src = get_node(li, ni)
            dst = get_node(li + 1, nj)
            width = random_edge_width()

            src_is_feature = is_feature(li, ni)
            dst_is_feature = is_feature(li + 1, nj)

            edges.append(
                {
                    "src": src,
                    "dst": dst,
                    "width": width,
                    "has_feature": src_is_feature or dst_is_feature,
                }
            )

# ─── Generate SVG ─────────────────────────────────────────────────────────────
gradient_defs = []
gradient_refs = {}

for i, e in enumerate(edges):
    if e["has_feature"]:
        gid = f"g{i}"
        s, d = e["src"], e["dst"]
        gradient_defs.append(
            f'    <linearGradient id="{gid}" x1="{s["x"]}" y1="{s["y"]}" '
            f'x2="{d["x"]}" y2="{d["y"]}" gradientUnits="userSpaceOnUse">\n'
            f'      <stop offset="0%" stop-color="{s["color"]}"/>'
            f'<stop offset="100%" stop-color="{d["color"]}"/>\n'
            f"    </linearGradient>"
        )
        gradient_refs[i] = gid

svg_lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">']

if gradient_defs:
    svg_lines.append("  <defs>")
    svg_lines.extend(gradient_defs)
    svg_lines.append("  </defs>")

# Draw edges (before nodes so nodes are on top)
for i, e in enumerate(edges):
    s, d = e["src"], e["dst"]
    if i in gradient_refs:
        stroke = f"url(#{gradient_refs[i]})"
    else:
        # Use the average-ish color: pick the source color for solid edges
        stroke = s["color"]
    svg_lines.append(
        f'  <line x1="{s["x"]}" y1="{s["y"]}" x2="{d["x"]}" y2="{d["y"]}" '
        f'stroke="{stroke}" stroke-width="{e["width"]}" stroke-linecap="round"/>'
    )

# Draw nodes
for n in nodes:
    svg_lines.append(f'  <circle cx="{n["x"]}" cy="{n["y"]}" r="{n["radius"]}" fill="{n["color"]}"/>')

svg_lines.append("</svg>")

svg_content = "\n".join(svg_lines)

output_path = "favicon.svg"
with open(output_path, "w") as f:
    f.write(svg_content)

print(f"Generated {output_path}")
print(f"  Layers: {LAYERS}")
print(f"  Nodes: {len(nodes)}")
print(f"  Edges: {len(edges)}")
print(f"  Feature node: layer {FEATURE_LAYER}, index {FEATURE_INDEX}")
