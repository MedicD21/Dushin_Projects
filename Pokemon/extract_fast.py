import json
import numpy as np
from PIL import Image

# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
BLE_PATH = "lumiose_city_BLE.png"
CLEAN_MAP_PATH = "lumiose_resized_clean.png"

ICONS = {
    "bench": "icon_bench.png",
    "ladder": "icon_ladder.png",
    "arrow": "icon_arrow.png",
}

# The offset you confirmed from GIMP
OFFSET_X = 15
OFFSET_Y = 21

THRESHOLD = 0.90  # similarity threshold (1.0 = perfect)
# -----------------------------------------------------


def load_img(path):
    """Load image as numpy array (RGB)."""
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def normalized_cross_correlation(big, tpl):
    """
    Fast normalized cross correlation using numpy broadcasting and stride tricks.
    Returns a 2D array of match scores.
    """
    H, W, C = big.shape
    h, w, _ = tpl.shape

    # Sliding window via stride tricks
    shape = (H - h + 1, W - w + 1, h, w, C)
    strides = big.strides[:2] + big.strides

    windows = np.lib.stride_tricks.as_strided(big, shape=shape, strides=strides)

    # Normalize template
    tpl_mean = tpl.mean()
    tpl_std = tpl.std() + 1e-6
    tpl_norm = (tpl - tpl_mean) / tpl_std

    # Normalize windows
    win_mean = windows.mean(axis=(2, 3, 4), keepdims=True)
    win_std = windows.std(axis=(2, 3, 4), keepdims=True) + 1e-6
    win_norm = (windows - win_mean) / win_std

    # Compute NCC
    ncc = (win_norm * tpl_norm).sum(axis=(2, 3, 4))
    ncc /= h * w * C

    return ncc


def find_icon_locations(big, tpl, label):
    print(f"\n🔍 Searching for: {label}...")
    ncc = normalized_cross_correlation(big, tpl)

    # Mask where score >= threshold
    ys, xs = np.where(ncc >= THRESHOLD)
    print(f" → Found {len(xs)} matches")

    return [{"x": int(x), "y": int(y), "type": label} for x, y in zip(xs, ys)]


def apply_offset(points):
    """Apply your GIMP offsets."""
    for p in points:
        p["x"] += OFFSET_X
        p["y"] += OFFSET_Y
    return points


# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
print("Loading images...")
ble = load_img(BLE_PATH)
clean = load_img(CLEAN_MAP_PATH)

all_points = []

for label, icon_path in ICONS.items():
    icon = load_img(icon_path)
    pts = find_icon_locations(ble, icon, label)
    pts = apply_offset(pts)
    all_points.extend(pts)

print("\nSaving markers.json...")
with open("markers_fast.json", "w") as f:
    json.dump(all_points, f, indent=4)

print("\n✅ Done! FAST markers saved to markers_fast.json")
