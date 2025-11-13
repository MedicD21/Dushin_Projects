import json
import numpy as np
from PIL import Image

BLE_PATH = "lumiose_city_BLE.png"
CLEAN_MAP_PATH = "lumiose_resized_clean.png"

ICONS = {
    "bench": "icon_bench.png",
    "ladder": "icon_ladder.png",
    "arrow": "icon_arrow.png",
}

OFFSET_X = 15
OFFSET_Y = 21

THRESHOLD = 0.90
TILE = 256  # tile size


def load_img(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def ncc_match(tile, icon):
    """Compute fast NCC inside a small tile."""
    H, W, C = tile.shape
    h, w, _ = icon.shape

    # Mean/std normalize icon
    icon_mean = icon.mean()
    icon_std = icon.std() + 1e-6
    icon_norm = (icon - icon_mean) / icon_std

    matches = []

    # Sliding window (tile is small, loops are fine)
    for y in range(H - h):
        for x in range(W - w):
            region = tile[y : y + h, x : x + w]

            r_mean = region.mean()
            r_std = region.std() + 1e-6
            region_norm = (region - r_mean) / r_std

            score = (region_norm * icon_norm).mean()

            if score >= THRESHOLD:
                matches.append((x, y))

    return matches


def scan_image(big, icon, label):
    H, W, _ = big.shape
    h, w, _ = icon.shape

    all_points = []

    for ty in range(0, H, TILE):
        for tx in range(0, W, TILE):
            # Extract tile
            tile = big[ty : ty + TILE + h, tx : tx + TILE + w]

            if tile.shape[0] < h or tile.shape[1] < w:
                continue  # skip incomplete tiles

            # Find matches in this tile
            hits = ncc_match(tile, icon)

            # Translate tile-local coords to global coords
            for x, y in hits:
                all_points.append(
                    {
                        "x": int(tx + x + OFFSET_X),
                        "y": int(ty + y + OFFSET_Y),
                        "type": label,
                    }
                )

        print(f" Scanned row {ty}/{H} for {label}")

    print(f" → Found {len(all_points)} {label} icons")
    return all_points


# -----------------------
# MAIN
# -----------------------
print("Loading images...")
ble = load_img(BLE_PATH)
clean = load_img(CLEAN_MAP_PATH)  # (only used for aligning offsets)

all_points = []

for label, icon_path in ICONS.items():
    print(f"\n🔍 Searching for {label} icons...")
    icon = load_img(icon_path)
    pts = scan_image(ble, icon, label)
    all_points.extend(pts)

print("\nSaving markers_tiles.json...")
with open("markers_tiles.json", "w") as f:
    json.dump(all_points, f, indent=4)

print("\n✅ DONE — output saved to markers_tiles.json")
