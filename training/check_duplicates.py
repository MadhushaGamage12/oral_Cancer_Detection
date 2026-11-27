import os
import hashlib
from collections import defaultdict

# DATASET PATH

DATASET_DIR = r"D:\Computer vision\basedata" # DATASET PATH (old Unclean dataset path)

splits = ["training", "validation", "testing"]
classes = ["cancer", "not_cancer"]

valid_extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".jfif"
)

# CREATE IMAGE HASH

def get_file_hash(file_path):
    """
    Creates a unique hash based on the actual file content.
    Files with exactly the same content will have the same hash.
    """
    hash_object = hashlib.md5()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            hash_object.update(data)
    return hash_object.hexdigest()

# COLLECT IMAGES

hash_to_files = defaultdict(list)
total_images = 0
print("=" * 70)
print("DUPLICATE IMAGE CHECK")
print("=" * 70)

for split in splits:
    for class_name in classes:
        folder = os.path.join(
            DATASET_DIR,
            split,
            class_name
        )

        if not os.path.exists(folder):
            print(
                f"WARNING: Folder not found -> "
                f"{folder}"
            )
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(
                folder,
                filename
            )

            if not os.path.isfile(file_path):
                continue
            if not filename.lower().endswith(valid_extensions):
                continue

            try:
                file_hash = get_file_hash(file_path)
                hash_to_files[file_hash].append(
                    file_path
                )
                total_images += 1

            except Exception as error:
                print(
                    f"Could not process: "
                    f"{file_path}"
                )
                print(error)


# FIND DUPLICATES

duplicate_groups = []
for file_hash, files in hash_to_files.items():
    if len(files) > 1:
        duplicate_groups.append(files)

# DISPLAY RESULTS

print()
print("=" * 70)
print("DUPLICATE CHECK RESULTS")
print("=" * 70)

print(f"Total images checked: {total_images}")

print(
    f"Duplicate groups found: "
    f"{len(duplicate_groups)}"
)

duplicate_file_count = sum(
    len(group)
    for group in duplicate_groups
)

print(
    f"Images involved in duplicates: "
    f"{duplicate_file_count}"
)

print("=" * 70)

# DISPLAY DUPLICATE FILES

if len(duplicate_groups) == 0:

    print()
    print("NO EXACT DUPLICATES FOUND.")
    print()

else:

    print()
    print("DUPLICATE GROUPS")
    print("=" * 70)

    for number, group in enumerate(
        duplicate_groups,
        start=1
    ):

        print()
        print(f"Duplicate Group {number}")
        print("-" * 70)

        for file_path in group:

            print(file_path)


# ============================================================
# IMPORTANT NOTE
# ============================================================

print()
print("=" * 70)
print("IMPORTANT")
print("=" * 70)

print(
    "No files were deleted or modified."
)

print(
    "This script only detects EXACT duplicate files."
)

print(
    "Resized, compressed, cropped, or slightly "
    "changed versions may not be detected."
)

print("=" * 70)