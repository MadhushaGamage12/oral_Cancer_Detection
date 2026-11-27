import os
from PIL import Image

DATASET_DIR = r"D:\Computer vision\basedata" # DATASET PATH (old Unclean dataset path)

splits = ["training", "validation", "testing"]
classes = ["cancer", "not_cancer"]

valid_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)

# DATASET CHECK

print("=" * 60)
print("ORAL CANCER DATASET CHECK")
print("=" * 60)

grand_total = 0

for split in splits:
    print()
    print(split.upper())
    print("-" * 60)
    split_total = 0

    for class_name in classes:
        folder_path = os.path.join(
            DATASET_DIR,
            split,
            class_name
        )

        if not os.path.exists(folder_path):
            print(f"{class_name}: FOLDER NOT FOUND")
            continue
        image_count = 0
        corrupted_count = 0
        other_file_count = 0

        for filename in os.listdir(folder_path):
            file_path = os.path.join(
                folder_path,
                filename
            )

            if not os.path.isfile(file_path):
                continue
            if not filename.lower().endswith(valid_extensions):
                other_file_count += 1
                continue
            try:
                with Image.open(file_path) as image:
                    image.verify()
                image_count += 1
            except Exception:
                corrupted_count += 1
        print(
            f"{class_name:12} : "
            f"{image_count} images | "
            f"Corrupted: {corrupted_count}"
        )

        if other_file_count > 0:
            print(
                f"{'':12}   Other files: "
                f"{other_file_count}"
            )

        split_total += image_count

    print("-" * 60)
    print(f"Total {split}: {split_total}")
    grand_total += split_total

# FINAL SUMMARY

print()
print("=" * 60)
print("FINAL DATASET SUMMARY")
print("=" * 60)
print(f"Total valid images: {grand_total}")
print("=" * 60)
