from PIL import Image
import json
import numpy as np

BLE_FILE = "lumiose_city_BLE.png"
OUT_JSON = "markers.json"

# Offsets from your GIMP alignment
OFFSET_X = 15
OFFSET_Y = 21


# Color thresholds
def is_black(px):
    return px[0] < 80 and px[1] < 80 and px[2] < 80


def is_gold(px):
    return px[0] > 150 and px[1] > 130 and px[2] < 80


def is_brown(px):
    return 80 < px[0] < 160 and 50 < px[1] < 120 and px[2] < 60


def is_white(px):
    return px[0] > 180 and px[1] > 180 and px[2] > 180


# Classification based on pixel patterns inside the circle
def classify_icon(region):
    arr = np.array(region)

    # Count pixel categories
    black = np.sum((arr[:, :, 0] < 80) & (arr[:, :, 1] < 80) & (arr[:, :, 2] < 80))
    gold = np.sum((arr[:, :, 0] > 150) & (arr[:, :, 1] > 130) & (arr[:, :, 2] < 80))
    brown = np.sum(
        (arr[:, :, 0] > 80)
        & (arr[:, :, 0] < 160)
        & (arr[:, :, 1] > 50)
        & (arr[:, :, 1] < 120)
        & (arr[:, :, 2] < 60)
    )
    white = np.sum((arr[:, :, 0] > 180) & (arr[:, :, 1] > 180) & (arr[:, :, 2] > 180))

    # ARROW → mostly gold
    if gold > 150:
        return "arrow"

    # LADDER → lots of white, arranged vertically
    if white > 200 and brown < 50:
        return "ladder"

    # BENCH → brown horizontal bars
    if brown > 120 and white < 120:
        return "bench"

    return "unknown"


def main():
    print("Loading BLE map...")
    img = Image.open(BLE_FILE).convert("RGB")
    w, h = img.size

    data = np.array(img)

    markers = []

    print("Scanning image for markers...")

    # Look for black circular borders (easy detection)
    for y in range(10, h - 10):
        for x in range(10, w - 10):
            px = data[y, x]

            # Find the outer white ring by looking for bright pixels next to dark ones
            if is_black(px):
                # Extract a small 24x24 area around it
                region = img.crop((x - 12, y - 12, x + 12, y + 12))

                # Skip if region is out of bounds
                if region.size != (24, 24):
                    continue

                icon_type = classify_icon(region)

                if icon_type != "unknown":
                    clean_x = x - OFFSET_X
                    clean_y = y - OFFSET_Y

                    markers.append(
                        {
                            "type": icon_type,
                            "ble_x": x,
                            "ble_y": y,
                            "clean_x": clean_x,
                            "clean_y": clean_y,
                        }
                    )

    print(f"Found {len(markers)} markers.")
    print("Saving markers.json...")
    with open(OUT_JSON, "w") as f:
        json.dump(markers, f, indent=4)

    print("Done!")


if __name__ == "__main__":
    main()
