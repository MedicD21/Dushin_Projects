from PIL import Image
import json
import os
import numpy as np

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------

BLE_MAP = "lumiose_city_BLE.png"
CLEAN_MAP = "lumiose_resized_clean.png"

ICON_BENCH = "icon_bench.png"
ICON_LADDER = "icon_ladder.png"
ICON_ARROW = "icon_arrow.png"

# Offset discovered from GIMP
OFFSET_X = 15
OFFSET_Y = 21

# Pixel match tolerance (0 = perfect, 30 = loose)
TOLERANCE = 25


# -------------------------------------------------------
# Helper: compute pixel difference
# -------------------------------------------------------
def patch_diff(a, b):
    a = np.asarray(a).astype(int)
    b = np.asarray(b).astype(int)
    return np.mean(np.abs(a - b))


# -------------------------------------------------------
# Template match without OpenCV
# -------------------------------------------------------
def find_icons(big_img, icon_img, icon_type):
    positions = []
    bw, bh = big_img.size
    iw, ih = icon_img.size

    big_np = np.asarray(big_img.convert("RGB"))
    icon_np = np.asarray(icon_img.convert("RGB"))

    for y in range(0, bh - ih):
        patch = big_np[y : y + ih, 0:iw]  # dummy slice
        # Instead of slicing column 0, do proper matching
        for x in range(0, bw - iw):
            patch = big_np[y : y + ih, x : x + iw]

            diff = np.mean(np.abs(patch - icon_np))

            if diff < TOLERANCE:
                positions.append({"type": icon_type, "x": x, "y": y})

    return positions


# -------------------------------------------------------
# Main
# -------------------------------------------------------
print("Loading maps...")
ble = Image.open(BLE_MAP).convert("RGB")

bench = Image.open(ICON_BENCH).convert("RGB")
ladder = Image.open(ICON_LADDER).convert("RGB")
arrow = Image.open(ICON_ARROW).convert("RGB")

print("Searching for icons...")

results = []
results += find_icons(ble, bench, "bench")
results += find_icons(ble, ladder, "ladder")
results += find_icons(ble, arrow, "arrow")

print(f"Found {len(results)} total markers.")

# -------------------------------------------------------
# Apply offset → convert BLE coordinate → clean map coordinate
# -------------------------------------------------------
for m in results:
    m["x"] = m["x"] - OFFSET_X
    m["y"] = m["y"] - OFFSET_Y

# -------------------------------------------------------
# Save output
# -------------------------------------------------------
with open("markers.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved markers.json")
