
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

# --------------------------------------------------
# 1. PATHS AND SETTINGS
# --------------------------------------------------

DATASET_DIR = r"D:\Computer vision\clean_dataset"

MODEL_PATH = (
    r"D:\FYP\training\results_efficientnet"
    r"\efficientnetb0_best.keras"
)

RESULTS_DIR = (
    r"D:\FYP\training\results_efficientnet"
    r"\evaluation_only"
)

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

VAL_DIR = os.path.join(DATASET_DIR, "validation")
TEST_DIR = os.path.join(DATASET_DIR, "testing")

# --------------------------------------------------
# 2. CHECK REQUIRED FILES AND FOLDERS
# --------------------------------------------------

for path in [MODEL_PATH, VAL_DIR, TEST_DIR]:

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required path not found: {path}"
        )

os.makedirs(RESULTS_DIR, exist_ok=True)

print("\nLoading saved EfficientNetB0 model...")

# Load without compiling or changing the saved model
model = keras.models.load_model(
    MODEL_PATH,
    compile=False
)

print("Model loaded successfully.")

# --------------------------------------------------
# 3. LOAD VALIDATION AND TESTING DATA
# --------------------------------------------------

datagen = ImageDataGenerator()

validation_generator = datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

test_generator = datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

# --------------------------------------------------
# 4. VERIFY CLASS MAPPING
# --------------------------------------------------

expected_mapping = {
    "cancer": 0,
    "not_cancer": 1
}

if validation_generator.class_indices != expected_mapping:
    raise ValueError(
        "Validation class mapping is incorrect. "
        f"Found: {validation_generator.class_indices}"
    )

if test_generator.class_indices != expected_mapping:
    raise ValueError(
        "Testing class mapping is incorrect. "
        f"Found: {test_generator.class_indices}"
    )

print("\nClass mapping verified:")
print(validation_generator.class_indices)

# --------------------------------------------------
# 5. EVALUATION FUNCTION
# --------------------------------------------------

def evaluate_dataset(generator, dataset_name):

    print(f"\nEvaluating {dataset_name} dataset...")

    generator.reset()

    # Model output represents NOT CANCER probability
    probabilities = model.predict(
        generator,
        verbose=1
    ).ravel()

    y_true = generator.classes

    if len(probabilities) != len(y_true):
        raise ValueError(
            f"{dataset_name}: Prediction count does not "
            "match the number of images."
        )

    if not np.all(np.isfinite(probabilities)):
        raise ValueError(
            f"{dataset_name}: Invalid prediction values found."
        )

    if np.any(probabilities < 0) or np.any(probabilities > 1):
        raise ValueError(
            f"{dataset_name}: Probabilities outside 0-1 range."
        )

    if len(np.unique(y_true)) != 2:
        raise ValueError(
            f"{dataset_name}: Both classes are required for evaluation."
        )

    # Output >= 0.5 means NOT CANCER (class 1)
    y_pred = (probabilities >= 0.5).astype(int)

    # Binary cross-entropy loss
    loss_values = tf.keras.losses.binary_crossentropy(
        y_true.astype("float32").reshape(-1, 1),
        probabilities.astype("float32").reshape(-1, 1)
    )

    loss = float(tf.reduce_mean(loss_values).numpy())

    # Classification metrics
    accuracy = accuracy_score(y_true, y_pred)

    # Cancer is class 0
    precision = precision_score(
        y_true, y_pred, pos_label=0, zero_division=0
    )

    recall = recall_score(
        y_true, y_pred, pos_label=0, zero_division=0
    )

    f1 = f1_score(
        y_true, y_pred, pos_label=0, zero_division=0
    )

    # Convert NOT CANCER probability to CANCER probability
    cancer_probabilities = 1.0 - probabilities

    cancer_actual = (y_true == 0).astype(int)

    auc = roc_auc_score(
        cancer_actual,
        cancer_probabilities
    )

    # Confusion matrix: Cancer first, Not Cancer second
    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )

    # Specificity for cancer classification
    specificity = (
        cm[1, 1] / (cm[1, 0] + cm[1, 1])
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["Cancer", "Not Cancer"],
        zero_division=0
    )

    results = {
        "Dataset": dataset_name,
        "Number of Images": len(y_true),
        "Loss": loss,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "Specificity": specificity,
        "ROC-AUC": auc
    }

    print("\n" + "=" * 50)
    print(f"{dataset_name.upper()} RESULTS")
    print("=" * 50)

    for key, value in results.items():

        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(report)

    return results, cm, report


# --------------------------------------------------
# 6. EVALUATE BOTH DATASETS
# --------------------------------------------------

validation_results, val_cm, val_report = evaluate_dataset(
    validation_generator,
    "Validation"
)

test_results, test_cm, test_report = evaluate_dataset(
    test_generator,
    "Testing"
)

# --------------------------------------------------
# 7. SAVE RESULTS SEPARATELY
# --------------------------------------------------

output_path = os.path.join(
    RESULTS_DIR,
    "efficientnet_evaluation_results.txt"
)

with open(output_path, "w", encoding="utf-8") as file:

    file.write("EFFICIENTNETB0 EVALUATION RESULTS\n")
    file.write("=" * 50 + "\n\n")

    for results, cm, report in [
        (validation_results, val_cm, val_report),
        (test_results, test_cm, test_report)
    ]:

        file.write(f"{results['Dataset'].upper()} RESULTS\n")
        file.write("-" * 40 + "\n")

        for key, value in results.items():

            if isinstance(value, float):
                file.write(f"{key}: {value:.4f}\n")
            else:
                file.write(f"{key}: {value}\n")

        file.write("\nConfusion Matrix:\n")
        file.write(str(cm))

        file.write("\n\nClassification Report:\n")
        file.write(report)
        file.write("\n\n")

print("\n" + "=" * 50)
print("EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 50)

print("\nResults saved at:")
print(output_path)
