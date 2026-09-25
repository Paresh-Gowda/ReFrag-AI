import cv2
import json
import random
import shutil
from pathlib import Path
import numpy as np

BASE = Path("reference_database")
CLEAN = BASE / "clean"
BROKEN = BASE / "broken"

BROKEN.mkdir(parents=True, exist_ok=True)

random.seed(42)
np.random.seed(42)

def damage_image(img, damage_type):
    out = img.copy()
    h, w = out.shape[:2]

    if damage_type == "missing_block":
        x1 = random.randint(0, w // 2)
        y1 = random.randint(0, h // 2)
        bw = random.randint(w // 8, w // 3)
        bh = random.randint(h // 8, h // 3)
        out[y1:y1+bh, x1:x1+bw] = 0

    elif damage_type == "multiple_blocks":
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, w - 20)
            y = random.randint(0, h - 20)
            bw = random.randint(20, max(21, w // 6))
            bh = random.randint(20, max(21, h // 6))
            out[y:min(y+bh, h), x:min(x+bw, w)] = 0

    elif damage_type == "blur":
        k = random.choice([11, 15, 21, 25])
        out = cv2.GaussianBlur(out, (k, k), 0)

    elif damage_type == "noise":
        noise = np.random.normal(0, 35, out.shape).astype(np.float32)
        out = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    elif damage_type == "scratches":
        for _ in range(random.randint(10, 25)):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            length = random.randint(20, max(21, w // 3))
            cv2.line(
                out,
                (x, y),
                (min(x + length, w - 1), min(y + random.randint(-5, 5), h - 1)),
                (0, 0, 0),
                random.randint(1, 4)
            )

    elif damage_type == "partial_corruption":
        for _ in range(random.randint(2, 4)):
            y = random.randint(0, h - 10)
            height = random.randint(5, max(6, h // 20))
            shift = random.randint(-80, 80)

            region = out[y:min(y+height, h)].copy()
            out[y:min(y+height, h)] = np.roll(region, shift, axis=1)

    elif damage_type == "jpeg_corruption":
        quality = random.choice([10, 15, 20])
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded = cv2.imencode(".jpg", out, encode_param)
        out = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

    elif damage_type == "darkened":
        out = (out.astype(np.float32) * random.uniform(0.35, 0.6)).clip(0, 255).astype(np.uint8)

    elif damage_type == "color_damage":
        channel = random.choice([0, 1, 2])
        out[:, :, channel] = (
            out[:, :, channel].astype(np.float32) *
            random.uniform(0.1, 0.35)
        ).astype(np.uint8)

    return out


damage_types = [
    "missing_block",
    "multiple_blocks",
    "blur",
    "noise",
    "scratches",
    "partial_corruption",
    "jpeg_corruption",
    "darkened",
    "color_damage",
]

clean_files = sorted(CLEAN.glob("*.jpg"))

if len(clean_files) < 100:
    raise RuntimeError(f"Expected 100 clean images, found {len(clean_files)}")

metadata = []

for i, clean_path in enumerate(clean_files[:100], start=1):
    img = cv2.imread(str(clean_path))

    if img is None:
        print(f"SKIP: {clean_path}")
        continue

    damage_type = damage_types[(i - 1) % len(damage_types)]

    # Make the damage deterministic but different for every image.
    random.seed(1000 + i)
    np.random.seed(1000 + i)

    broken = damage_image(img, damage_type)

    broken_path = BROKEN / f"{i:03d}_broken.jpg"
    cv2.imwrite(str(broken_path), broken)

    metadata.append({
        "id": f"{i:03d}",
        "clean_image": str(clean_path),
        "broken_image": str(broken_path),
        "damage_type": damage_type,
        "status": "synthetically_damaged",
    })

    print(f"[{i:03d}/100] {damage_type}")

with open(BASE / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print()
print("=" * 60)
print("REFERENCE DATABASE CREATED")
print("=" * 60)
print(f"Clean images : {len(clean_files[:100])}")
print(f"Broken images: {len(metadata)}")
print(f"Metadata     : {BASE / 'metadata.json'}")
