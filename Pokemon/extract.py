from PIL import Image
import json
import math


# -------------------------------------------------------
# RMS difference helper (how different two images are)
# -------------------------------------------------------
def rmsdiff(im1, im2):
    """
    Calculate RMS (Root Mean Square) pixel difference between two images.
    Lower = more similar. 0 = perfect match.
    """
    if im1.size != im2.size:
        return 999999

    diff_sum = 0
    count = im1.size[0] * im1.size[1]

    px1 = im1.load()
    px2 = im2.load()

    for y in range(im1.size[1]):
        for x in range(im1.size[0]):
            diff_sum += (px1[x, y] - px2[x, y]) ** 2

    return math.sqrt(diff_sum / count)


# -------------------------------------------------------
# Slide the template over the map and find matches
# -------------------------------------------------------
def find_template(big_img, icon_img, threshold):
    """
    Scan `big_img` for occurrences of `icon_img`.
    Returns list of (x, y) icon-center coordinates.
    """
    big = big_img.convert("L")  # grayscale for comparison
    icon = icon_img.convert("L")
    W, H = big.size
    w, h = icon.size

    results = []

    for y in range(0, H - h):
        for x in range(0, W - w):
            area = big.crop((x, y, x + w, y + h))
            diff = rmsdiff(icon, area)

            if diff < threshold:
                # center coordinate
                results.append(
                    {
                        "x": x + w / 2,
                        "y": y + h / 2,
                        "diff": diff,
                    }
                )

    return results


# -------------------------------------------------------
# MAIN SCRIPT
# -------------------------------------------------------
if __name__ == "__main__":
    print("Loading map...")
    map_img = Image.open("lumiose_stitched.png")

    print("Loading icons...")
    bench_icon = Image.open("icon_bench.png")
    ladder_icon = Image.open("icon_ladder.png")
    arrow_icon = Image.open("icon_arrow.png")

    print("Searching for benches...")
    benches = find_template(map_img, bench_icon, threshold=12)

    print("Searching for ladders...")
    ladders = find_template(map_img, ladder_icon, threshold=12)

    print("Searching for arrows...")
    arrows = find_template(map_img, arrow_icon, threshold=14)

    print("Saving JSON...")
    data = {"bench": benches, "ladder": ladders, "arrow": arrows}

    with open("lumiose_points.json", "w") as f:
        json.dump(data, f, indent=2)

    print("\nDone! Saved: lumiose_points.json\n")
