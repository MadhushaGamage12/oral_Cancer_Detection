import os
from collections import Counter

DATASET_DIR = r"D:\Computer vision\basedata" # DATASET PATH (old Unclean dataset path)

splits = ["training", "validation", "testing"]
classes = ["cancer", "not_cancer"]

print("=" * 60)
print("IMAGE FILE EXTENSION CHECK")
print("=" * 60)

grand_total = 0

for split in splits:

    print()
    print(split.upper())
    print("-" * 60)

    for class_name in classes:

        folder = os.path.join(
            DATASET_DIR,
            split,
            class_name
        )

        if not os.path.exists(folder):
            print(f"{class_name}: FOLDER NOT FOUND")
            continue

        extensions = Counter()
        total_files = 0

        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                total_files += 1
                _, extension = os.path.splitext(filename)
                if extension:
                    extensions[extension.lower()] += 1
                else:
                    extensions["NO EXTENSION"] += 1

        print(f"\n{class_name}")
        print(f"Total files: {total_files}")

        for extension, count in extensions.items():
            print(f"  {extension}: {count}")

        grand_total += total_files

print()
print("=" * 60)
print(f"TOTAL FILES: {grand_total}")
print("=" * 60)