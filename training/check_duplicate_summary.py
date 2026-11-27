import os
import hashlib
from collections import defaultdict

DATASET_DIR = r"D:\Computer vision\basedata"  # DATASET PATH (old Unclean dataset path)

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

def get_file_hash(file_path):
    hash_object = hashlib.md5()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(8192)
            if not data:
                break
            hash_object.update(data)
    return hash_object.hexdigest()

# Collect files

hash_to_files = defaultdict(list)
for split in splits:
    for class_name in classes:
        folder = os.path.join(
            DATASET_DIR,
            split,
            class_name
        )

        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if not os.path.isfile(file_path):
                continue
            if not filename.lower().endswith(valid_extensions):
                continue
            file_hash = get_file_hash(file_path)
            hash_to_files[file_hash].append(file_path)

# Analyse duplicate groups

same_split = 0
train_validation = 0
train_testing = 0
validation_testing = 0

print("=" * 70)
print("DUPLICATE GROUP SUMMARY")
print("=" * 70)

for group_number, files in enumerate(
    [files for files in hash_to_files.values() if len(files) > 1],
    start=1
):
    group_splits = set()

    for file_path in files:
        relative = os.path.relpath(
            file_path,
            DATASET_DIR
        )

        split = relative.split(os.sep)[0]
        group_splits.add(split)
    if len(group_splits) == 1:
        same_split += 1
    elif "training" in group_splits and "validation" in group_splits:
        train_validation += 1
    elif "training" in group_splits and "testing" in group_splits:
        train_testing += 1
    elif "validation" in group_splits and "testing" in group_splits:
        validation_testing += 1

# Results

total_duplicate_groups = sum(
    1
    for files in hash_to_files.values()
    if len(files) > 1
)

print(f"Total duplicate groups       : {total_duplicate_groups}")
print(f"Same split duplicates        : {same_split}")
print(f"Training + Validation        : {train_validation}")
print(f"Training + Testing           : {train_testing}")
print(f"Validation + Testing         : {validation_testing}")

print("=" * 70)

print()
print("NO FILES WERE DELETED OR MOVED.")
print("This script only analyses the duplicate groups.")
print("=" * 70)