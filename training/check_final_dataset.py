import os

DATASET_DIR = r"D:\Computer vision\clean_dataset"

classes = ["cancer", "not_cancer"]
splits = ["training", "validation", "testing"]

total_all = 0

print("=" * 70)
print("FINAL CLEAN DATASET CHECK")
print("=" * 70)

for split in splits:
    split_total = 0

    print(f"\n{split.upper()}")
    print("-" * 40)

    for class_name in classes:
        folder = os.path.join(DATASET_DIR, split, class_name)

        if not os.path.exists(folder):
            print(f"{class_name}: FOLDER NOT FOUND")
            continue

        count = 0

        for file in os.listdir(folder):
            if file.lower().endswith(
                (".jpg", ".jpeg", ".png", ".webp", ".jfif")
            ):
                count += 1

        print(f"{class_name}: {count}")

        split_total += count
        total_all += count

    print(f"Split Total: {split_total}")

print("\n" + "=" * 70)
print(f"TOTAL FINAL WORKING DATASET: {total_all}")
print("=" * 70)