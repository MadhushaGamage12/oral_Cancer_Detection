import os
import shutil
import hashlib
from collections import defaultdict

# PATHS

SOURCE_DIR = r"D:\Computer vision\basedata" #old data set path
CLEAN_DIR = r"D:\Computer vision\clean_dataset"  #clean dataset path

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

# HASH FUNCTION

def get_file_hash(file_path):

    hash_object = hashlib.md5()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(8192)

            if not data:
                break

            hash_object.update(data)

    return hash_object.hexdigest()


# COLLECT ALL IMAGES

hash_to_files = defaultdict(list)
total_images = 0

print("=" * 70)
print("CREATING CLEAN DATASET")
print("=" * 70)

for split in splits:
    for class_name in classes:
        folder = os.path.join(
            SOURCE_DIR,
            split,
            class_name
        )

        if not os.path.exists(folder):
            print(f"WARNING: Missing folder: {folder}")
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if not os.path.isfile(file_path):
                continue

            if not filename.lower().endswith(valid_extensions):
                continue

            file_hash = get_file_hash(file_path)

            hash_to_files[file_hash].append(
                file_path
            )

            total_images += 1


print(f"Original images found: {total_images}")

# DETERMINE WHICH FILES TO KEEP

files_to_keep = set()

duplicate_files = set()

for file_hash, files in hash_to_files.items():

    if len(files) == 1:

        # No duplicate
        files_to_keep.add(files[0])
        continue

    
    # Determine priority
    # Testing > Validation > Training

    testing_files = [
        f for f in files
        if os.sep + "testing" + os.sep in f
    ]

    validation_files = [
        f for f in files
        if os.sep + "validation" + os.sep in f
    ]

    training_files = [
        f for f in files
        if os.sep + "training" + os.sep in f
    ]

    if testing_files:

        keep_file = testing_files[0]

    elif validation_files:

        keep_file = validation_files[0]

    else:

        keep_file = training_files[0]

    files_to_keep.add(keep_file)

    for file_path in files:

        if file_path != keep_file:

            duplicate_files.add(file_path)


# CREATE CLEAN DATASET DIRECTORIES

print()
print("Creating clean dataset folders...")
for split in splits:
    for class_name in classes:
        folder = os.path.join(
            CLEAN_DIR,
            split,
            class_name
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

# COPY KEPT FILES

copied_count = 0

for file_path in files_to_keep:

    relative_path = os.path.relpath(
        file_path,
        SOURCE_DIR
    )

    destination = os.path.join(
        CLEAN_DIR,
        relative_path
    )

    os.makedirs(
        os.path.dirname(destination),
        exist_ok=True
    )

    shutil.copy2(
        file_path,
        destination
    )

    copied_count += 1

# FINAL COUNT

print()
print("=" * 70)
print("CLEAN DATASET CREATED")
print("=" * 70)

print(f"Original images : {total_images}")
print(f"Duplicates removed from clean copy : {len(duplicate_files)}")
print(f"Clean images     : {copied_count}")

print("=" * 70)

# COUNT EACH SPLIT / CLASS
print()
print("CLEAN DATASET SUMMARY")
print("-" * 70)

grand_total = 0

for split in splits:

    split_total = 0

    for class_name in classes:

        folder = os.path.join(
            CLEAN_DIR,
            split,
            class_name
        )

        count = 0

        if os.path.exists(folder):

            for filename in os.listdir(folder):

                file_path = os.path.join(
                    folder,
                    filename
                )

                if os.path.isfile(file_path):

                    if filename.lower().endswith(
                        valid_extensions
                    ):
                        count += 1

        print(
            f"{split:12} | "
            f"{class_name:12} | "
            f"{count}"
        )

        split_total += count

    print(
        f"{'':12} | "
        f"{'TOTAL':12} | "
        f"{split_total}"
    )

    print("-" * 70)

    grand_total += split_total


print(f"FINAL CLEAN DATASET TOTAL: {grand_total}")

print()
print("Original dataset was NOT modified.")
print("Clean dataset location:")
print(CLEAN_DIR)

print("=" * 70)