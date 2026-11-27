# FULL MODEL COMPARISON
# Models:
# 1. Baseline CNN
# 2. MobileNetV2
# 3. EfficientNetB0
# 4. ResNet50
# 5. VGG16

# This script:
# - Does NOT train models again
# - Does NOT modify .keras model files
# - Reads existing result files
# - Compares all 5 trained models
# - Creates CSV and TXT comparison reports
# - Identifies the best-performing model

import os
import re
import csv

# 1. MAIN TRAINING FOLDER
TRAINING_DIR = r"D:\FYP\training"

# 2. MODEL RESULT FOLDERS

BASELINE_DIR = os.path.join(
    TRAINING_DIR,
    "results_baseline"
)

MOBILENET_DIR = os.path.join(
    TRAINING_DIR,
    "results_mobilenet"
)

EFFICIENTNET_DIR = os.path.join(
    TRAINING_DIR,
    "results_efficientnet"
)

RESNET50_DIR = os.path.join(
    TRAINING_DIR,
    "results_resnet50"
)

VGG16_DIR = os.path.join(
    TRAINING_DIR,
    "results_vgg16"
)


# 3. COMPARISON OUTPUT FOLDER

COMPARISON_DIR = os.path.join(
    TRAINING_DIR,
    "model_comparison"
)

os.makedirs(
    COMPARISON_DIR,
    exist_ok=True
)


# 4. RESULT FILE PATHS
# Existing result files are read only They are NOT modified. If a filename is slightly different, the script will automatically search for the first .txt file inside the relevant result folder.

def find_result_file(folder, expected_filename):
    # First check the expected filename.

    expected_path = os.path.join(
        folder,
        expected_filename
    )

    if os.path.exists(expected_path):

        return expected_path

    # If the expected filename is not found,
    # search for any TXT file in the folder.

    if os.path.exists(folder):
        txt_files = [
            file for file in os.listdir(folder)
            if file.lower().endswith(".txt")
        ]

        if len(txt_files) > 0:
            return os.path.join(
                folder,
                txt_files[0]
            )

    return None

baseline_results = find_result_file(
    BASELINE_DIR,
    "baseline_results.txt"
)

mobilenet_results = find_result_file(
    MOBILENET_DIR,
    "mobilenet_results.txt"
)

efficientnet_results = find_result_file(
    EFFICIENTNET_DIR,
    "efficientnetb0_results.txt"
)

resnet50_results = find_result_file(
    RESNET50_DIR,
    "resnet50_results.txt"
)

vgg16_results = find_result_file(
    VGG16_DIR,
    "vgg16_results.txt"
)

# 5. READ RESULT FILE

def read_file(file_path):

    if file_path is None:

        return ""

    if not os.path.exists(file_path):

        print()
        print("WARNING: Result file not found:")
        print(file_path)
        return ""

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# 6. EXTRACT NUMBER

def extract_number(text, pattern):

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return float(
            match.group(1)
        )

    return None


# 7. READ ALL MODEL RESULTS

print()
print("=" * 75)
print("READING MODEL RESULTS")
print("=" * 75)


baseline_text = read_file(
    baseline_results
)

mobilenet_text = read_file(
    mobilenet_results
)

efficientnet_text = read_file(
    efficientnet_results
)

resnet50_text = read_file(
    resnet50_results
)

vgg16_text = read_file(
    vgg16_results
)

# 8. EXTRACT METRICS

def extract_metrics(text):

    accuracy = extract_number(
        text,
        r"Accuracy\s*:\s*([0-9.]+)"
    )

    precision = extract_number(
        text,
        r"Precision\s*:\s*([0-9.]+)"
    )

    recall = extract_number(
        text,
        r"Recall\s*:\s*([0-9.]+)"
    )

    f1 = extract_number(
        text,
        r"F1[- ]score\s*:\s*([0-9.]+)"
    )

    return (
        accuracy,
        precision,
        recall,
        f1
    )


baseline_accuracy, baseline_precision, baseline_recall, baseline_f1 = extract_metrics(
    baseline_text
)

mobilenet_accuracy, mobilenet_precision, mobilenet_recall, mobilenet_f1 = extract_metrics(
    mobilenet_text
)

efficientnet_accuracy, efficientnet_precision, efficientnet_recall, efficientnet_f1 = extract_metrics(
    efficientnet_text
)

resnet50_accuracy, resnet50_precision, resnet50_recall, resnet50_f1 = extract_metrics(
    resnet50_text
)

vgg16_accuracy, vgg16_precision, vgg16_recall, vgg16_f1 = extract_metrics(
    vgg16_text
)

# 9. MODEL INFORMATION
# All five models use:
# Input Size    : 224 x 224
# Augmentation  : Yes
#
# Parameters and training times are NOT guessed.
# If they were not recorded in the result files,
# they are marked as "Not recorded".


model_data = [

    {
        "Model": "Baseline CNN",
        "Parameters": "Not recorded",
        "Input Size": "224 x 224",
        "Augmentation": "Yes",
        "Training Time": "Not recorded",
        "Accuracy": baseline_accuracy,
        "Precision": baseline_precision,
        "Recall": baseline_recall,
        "F1-Score": baseline_f1
    },

    {
        "Model": "MobileNetV2",
        "Parameters": "Not recorded",
        "Input Size": "224 x 224",
        "Augmentation": "Yes",
        "Training Time": "Not recorded",
        "Accuracy": mobilenet_accuracy,
        "Precision": mobilenet_precision,
        "Recall": mobilenet_recall,
        "F1-Score": mobilenet_f1
    },

    {
        "Model": "EfficientNetB0",
        "Parameters": "Not recorded",
        "Input Size": "224 x 224",
        "Augmentation": "Yes",
        "Training Time": "2.52 minutes",
        "Accuracy": efficientnet_accuracy,
        "Precision": efficientnet_precision,
        "Recall": efficientnet_recall,
        "F1-Score": efficientnet_f1
    },

    {
        "Model": "ResNet50",
        "Parameters": "Not recorded",
        "Input Size": "224 x 224",
        "Augmentation": "Yes",
        "Training Time": "Not recorded",
        "Accuracy": resnet50_accuracy,
        "Precision": resnet50_precision,
        "Recall": resnet50_recall,
        "F1-Score": resnet50_f1
    },

    {
        "Model": "VGG16",
        "Parameters": "Not recorded",
        "Input Size": "224 x 224",
        "Augmentation": "Yes",
        "Training Time": "Not recorded",
        "Accuracy": vgg16_accuracy,
        "Precision": vgg16_precision,
        "Recall": vgg16_recall,
        "F1-Score": vgg16_f1
    }

]

# 10. DISPLAY MODEL COMPARISON

print()
print("=" * 120)
print("FULL MODEL COMPARISON")
print("=" * 120)

print(
    f"{'Model':<20}"
    f"{'Accuracy':<15}"
    f"{'Precision':<15}"
    f"{'Recall':<15}"
    f"{'F1-Score':<15}"
)

print("-" * 120)


for model in model_data:

    print(
        f"{model['Model']:<20}"
        f"{str(model['Accuracy']):<15}"
        f"{str(model['Precision']):<15}"
        f"{str(model['Recall']):<15}"
        f"{str(model['F1-Score']):<15}"
    )


print("=" * 120)

# 11. FIND BEST MODEL
#
# F1-score is used as the main criterion because it balances  precision and recall.
# This is particularly useful for medical classification, where both false positives and false negatives are important.


valid_models = [
    model for model in model_data
    if model["F1-Score"] is not None
]


if len(valid_models) > 0:

    best_model = max(
        valid_models,
        key=lambda model: model["F1-Score"]
    )

    print()
    print("=" * 75)
    print("BEST-PERFORMING MODEL")
    print("=" * 75)

    print(
        f"Model      : {best_model['Model']}"
    )

    print(
        f"Accuracy   : {best_model['Accuracy']}"
    )

    print(
        f"Precision  : {best_model['Precision']}"
    )

    print(
        f"Recall     : {best_model['Recall']}"
    )

    print(
        f"F1-Score   : {best_model['F1-Score']}"
    )

    print("=" * 75)

else:
    best_model = None
    print()
    print("WARNING: No valid F1-score values found.")

# 12. SAVE CSV REPORT

csv_path = os.path.join(
    COMPARISON_DIR,
    "model_comparison.csv"
)

with open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "Model",
            "Parameters",
            "Input Size",
            "Augmentation",
            "Training Time",
            "Accuracy",
            "Precision",
            "Recall",
            "F1-Score"
        ]
    )

    writer.writeheader()

    writer.writerows(
        model_data
    )

# 13. SAVE TXT REPORT

txt_path = os.path.join(
    COMPARISON_DIR,
    "model_comparison.txt"
)

with open(
    txt_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "ORAL CANCER DETECTION - FULL MODEL COMPARISON\n"
    )

    file.write(
        "=" * 80 + "\n\n"
    )

    file.write(
        "Models Compared:\n"
    )

    file.write(
        "1. Baseline CNN\n"
    )

    file.write(
        "2. MobileNetV2\n"
    )

    file.write(
        "3. EfficientNetB0\n"
    )

    file.write(
        "4. ResNet50\n"
    )

    file.write(
        "5. VGG16\n\n"
    )

    file.write(
        "=" * 80 + "\n\n"
    )


    for model in model_data:

        file.write(
            f"Model         : {model['Model']}\n"
        )

        file.write(
            f"Parameters    : {model['Parameters']}\n"
        )

        file.write(
            f"Input Size    : {model['Input Size']}\n"
        )

        file.write(
            f"Augmentation  : {model['Augmentation']}\n"
        )

        file.write(
            f"Training Time : {model['Training Time']}\n"
        )

        file.write(
            f"Accuracy      : {model['Accuracy']}\n"
        )

        file.write(
            f"Precision     : {model['Precision']}\n"
        )

        file.write(
            f"Recall        : {model['Recall']}\n"
        )

        file.write(
            f"F1-Score      : {model['F1-Score']}\n"
        )

        file.write(
            "-" * 80 + "\n"
        )


    # BEST MODEL

    if best_model is not None:

        file.write("\n")

        file.write(
            "BEST-PERFORMING MODEL\n"
        )

        file.write(
            "=" * 80 + "\n"
        )

        file.write(
            f"Model      : {best_model['Model']}\n"
        )

        file.write(
            f"Accuracy   : {best_model['Accuracy']}\n"
        )

        file.write(
            f"Precision  : {best_model['Precision']}\n"
        )

        file.write(
            f"Recall     : {best_model['Recall']}\n"
        )

        file.write(
            f"F1-Score   : {best_model['F1-Score']}\n"
        )


# 14. FINAL MESSAGE

print()
print("=" * 75)
print("FULL MODEL COMPARISON COMPLETED SUCCESSFULLY")
print("=" * 75)

print()
print("Compared Models:")
print("1. Baseline CNN")
print("2. MobileNetV2")
print("3. EfficientNetB0")
print("4. ResNet50")
print("5. VGG16")

print()
print("Comparison CSV saved to:")
print(csv_path)

print()
print("Comparison TXT report saved to:")
print(txt_path)

print()
print("Existing individual model result files were NOT modified.")

print()
print("No models were retrained.")

print("=" * 75)