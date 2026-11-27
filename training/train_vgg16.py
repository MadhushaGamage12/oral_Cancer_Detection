# ============================================================
# VGG16 - Oral Cancer Classification
# ============================================================
# Me script eken:
# 1. Clean dataset eka load karanawa
# 2. Image augmentation apply karanawa
# 3. ImageNet pretrained VGG16 model eka load karanawa
# 4. VGG16 base eka freeze karala classification head eka train karanawa
# 5. Best model saha final model save karanawa
# 6. Accuracy / Loss graphs save karanawa
# 7. Confusion matrix generate karanawa
# 8. Accuracy, Precision, Recall, F1-score calculate karanawa
# 9. Training time record karanawa
# 10. Model parameters record karanawa
# ============================================================

import os
import time
import numpy as np
import tensorflow as tf

from tensorflow.keras import layers, models
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing import image_dataset_from_directory

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

import matplotlib.pyplot as plt


# ============================================================
# 1. Dataset paths
# ============================================================

# Ape clean dataset eke paths
TRAIN_DIR = r"D:\Computer vision\basedata\training"
VAL_DIR = r"D:\Computer vision\basedata\validation"
TEST_DIR = r"D:\Computer vision\basedata\testing"

# VGG16 results save karana folder eka
RESULTS_DIR = r"D:\FYP\training\results_vgg16"

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# 2. Basic settings
# ============================================================

# VGG16 ekata use karana image size eka 224 x 224
IMG_SIZE = (224, 224)

# Dataset eke batch size
BATCH_SIZE = 32

# Maximum training epochs
EPOCHS = 20

# Random seed eka set karanne reproducibility ekata
SEED = 42


# ============================================================
# 3. Load datasets
# ============================================================

print("\nLoading datasets...")

train_ds = image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

val_ds = image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

test_ds = image_dataset_from_directory(
    TEST_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# Dataset eke class names
class_names = train_ds.class_names

print("\nClass names:", class_names)

print("\nDataset loaded successfully.")


# ============================================================
# 4. Performance optimization
# ============================================================

# Dataset loading eka faster karanna cache + prefetch use karanawa
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
test_ds = test_ds.prefetch(buffer_size=AUTOTUNE)


# ============================================================
# 5. Data augmentation
# ============================================================

# Training images walata random transformations apply karanawa.
# Me transformations overfitting adu karanna help karanawa.
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
], name="data_augmentation")


# ============================================================
# 6. Load pretrained VGG16
# ============================================================

print("\nLoading pretrained VGG16...")

# VGG16 ImageNet pretrained weights use karanawa.
#
# include_top=False kiyanne original VGG16 classification
# layers remove karala convolutional feature extractor eka
# witharak gannawa.
base_model = VGG16(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

# Pretrained VGG16 weights initially freeze karanawa.
# E nisa me weights training eke update wenne naha.
base_model.trainable = False

print("VGG16 loaded successfully.")


# ============================================================
# 7. Build VGG16 classification model
# ============================================================

inputs = layers.Input(shape=(224, 224, 3))

# Training images walata augmentation apply karanawa
x = data_augmentation(inputs)

# VGG16 pretrained feature extractor
x = base_model(x, training=False)

# Feature maps tika single vector ekakata convert karanawa
x = layers.GlobalAveragePooling2D()(x)

# Small classification layer
x = layers.Dense(128, activation="relu")(x)

# Dropout overfitting adu karanna use karanawa
x = layers.Dropout(0.5)(x)

# Binary classification:
# 0 = cancer
# 1 = not_cancer
outputs = layers.Dense(1, activation="sigmoid")(x)

# Final model
model = models.Model(inputs, outputs)


# ============================================================
# 8. Compile model
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)


# ============================================================
# 9. Display model summary
# ============================================================

print("\n================ MODEL SUMMARY ================\n")

model.summary()


# ============================================================
# 10. Calculate model parameters
# ============================================================

# Total parameters
total_params = model.count_params()

# Trainable parameters
trainable_params = np.sum([
    tf.keras.backend.count_params(weight)
    for weight in model.trainable_weights
])

# Non-trainable parameters
non_trainable_params = total_params - trainable_params

print("\n================ PARAMETERS ================\n")

print(f"Total Parameters      : {total_params:,}")
print(f"Trainable Parameters  : {trainable_params:,}")
print(f"Non-trainable Params  : {non_trainable_params:,}")


# ============================================================
# 11. Callbacks
# ============================================================

# Best validation accuracy thiyena model eka save karanawa
best_model_path = os.path.join(
    RESULTS_DIR,
    "vgg16_best.keras"
)

checkpoint = tf.keras.callbacks.ModelCheckpoint(
    best_model_path,
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)


# Validation accuracy improve nowunoth training nawaththanna
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy",
    patience=5,
    restore_best_weights=True,
    verbose=1
)


# ============================================================
# 12. Train the model
# ============================================================

print("\n================================================")
print("Starting VGG16 training...")
print("================================================\n")

# Training start time
start_time = time.time()

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[
        checkpoint,
        early_stopping
    ]
)

# Training end time
end_time = time.time()

# Total training time in minutes
training_time_seconds = end_time - start_time
training_time_minutes = training_time_seconds / 60

print("\n================================================")
print(f"Training completed in {training_time_minutes:.2f} minutes")
print("================================================")


# ============================================================
# 13. Save final model
# ============================================================

final_model_path = os.path.join(
    RESULTS_DIR,
    "vgg16_final.keras"
)

model.save(final_model_path)

print(f"\nFinal model saved to:")
print(final_model_path)


# ============================================================
# 14. Plot Accuracy
# ============================================================

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["accuracy"],
    label="Training Accuracy"
)

plt.plot(
    history.history["val_accuracy"],
    label="Validation Accuracy"
)

plt.title("VGG16 Accuracy")

plt.xlabel("Epoch")

plt.ylabel("Accuracy")

plt.legend()

plt.grid(True)

accuracy_graph_path = os.path.join(
    RESULTS_DIR,
    "accuracy_graph.png"
)

plt.savefig(
    accuracy_graph_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nAccuracy graph saved.")


# ============================================================
# 15. Plot Loss
# ============================================================

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["loss"],
    label="Training Loss"
)

plt.plot(
    history.history["val_loss"],
    label="Validation Loss"
)

plt.title("VGG16 Loss")

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.legend()

plt.grid(True)

loss_graph_path = os.path.join(
    RESULTS_DIR,
    "loss_graph.png"
)

plt.savefig(
    loss_graph_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Loss graph saved.")


# ============================================================
# 16. Evaluate on test dataset
# ============================================================

print("\n================================================")
print("Evaluating VGG16 on test dataset...")
print("================================================\n")

test_loss, test_accuracy = model.evaluate(
    test_ds,
    verbose=1
)


# ============================================================
# 17. Get predictions
# ============================================================

y_true = []
y_prob = []

# Test images walin true labels saha prediction probabilities
for images, labels in test_ds:

    predictions = model.predict(
        images,
        verbose=0
    )

    y_true.extend(labels.numpy())
    y_prob.extend(predictions.flatten())


# NumPy arrays walata convert karanawa
y_true = np.array(y_true)
y_prob = np.array(y_prob)


# Sigmoid probability eka 0.5 threshold eken class ekakata convert karanawa
y_pred = (y_prob >= 0.5).astype(int)


# ============================================================
# 18. Calculate evaluation metrics
# ============================================================

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)


# ============================================================
# 19. Confusion Matrix
# ============================================================

cm = confusion_matrix(
    y_true,
    y_pred
)

print("\n================ CONFUSION MATRIX ================\n")

print(cm)


# Confusion matrix image eka save karanawa
plt.figure(figsize=(7, 6))

plt.imshow(cm)

plt.title("VGG16 Confusion Matrix")

plt.xlabel("Predicted Label")

plt.ylabel("True Label")

plt.xticks(
    [0, 1],
    class_names
)

plt.yticks(
    [0, 1],
    class_names
)

# Matrix values image eke pennanawa
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )

plt.colorbar()

plt.tight_layout()

cm_path = os.path.join(
    RESULTS_DIR,
    "confusion_matrix.png"
)

plt.savefig(
    cm_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Confusion matrix saved.")


# ============================================================
# 20. Classification Report
# ============================================================

report = classification_report(
    y_true,
    y_pred,
    target_names=class_names,
    zero_division=0
)

print("\n================ CLASSIFICATION REPORT ================\n")

print(report)


# ============================================================
# 21. Save results to text file
# ============================================================

results_path = os.path.join(
    RESULTS_DIR,
    "vgg16_results.txt"
)

with open(results_path, "w") as f:

    f.write("VGG16 ORAL CANCER CLASSIFICATION RESULTS\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"Input Size           : 224 x 224\n")
    f.write(f"Batch Size           : {BATCH_SIZE}\n")
    f.write(f"Maximum Epochs       : {EPOCHS}\n")
    f.write(f"Augmentation         : Yes\n")
    f.write(f"Pretrained Weights   : ImageNet\n")
    f.write(f"Base Model Frozen    : Yes\n\n")

    f.write("MODEL PARAMETERS\n")
    f.write("-" * 60 + "\n")
    f.write(f"Total Parameters     : {total_params:,}\n")
    f.write(f"Trainable Parameters : {trainable_params:,}\n")
    f.write(f"Non-trainable Params : {non_trainable_params:,}\n\n")

    f.write("TRAINING TIME\n")
    f.write("-" * 60 + "\n")
    f.write(
        f"Training Time        : "
        f"{training_time_minutes:.2f} minutes\n\n"
    )

    f.write("TEST RESULTS\n")
    f.write("-" * 60 + "\n")

    f.write(
        f"Test Loss            : "
        f"{test_loss:.4f}\n"
    )

    f.write(
        f"Accuracy             : "
        f"{accuracy:.4f} ({accuracy * 100:.2f}%)\n"
    )

    f.write(
        f"Precision            : "
        f"{precision:.4f} ({precision * 100:.2f}%)\n"
    )

    f.write(
        f"Recall               : "
        f"{recall:.4f} ({recall * 100:.2f}%)\n"
    )

    f.write(
        f"F1-score             : "
        f"{f1:.4f} ({f1 * 100:.2f}%)\n\n"
    )

    f.write("CONFUSION MATRIX\n")
    f.write("-" * 60 + "\n")
    f.write(str(cm) + "\n\n")

    f.write("CLASSIFICATION REPORT\n")
    f.write("-" * 60 + "\n")
    f.write(report)


# ============================================================
# 22. Final output
# ============================================================

print("\n================================================")
print("VGG16 TRAINING COMPLETED SUCCESSFULLY")
print("================================================")

print(f"\nAccuracy  : {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Precision : {precision:.4f} ({precision * 100:.2f}%)")
print(f"Recall    : {recall:.4f} ({recall * 100:.2f}%)")
print(f"F1-score  : {f1:.4f} ({f1 * 100:.2f}%)")

print(f"\nTraining Time : {training_time_minutes:.2f} minutes")

print("\nResults saved in:")
print(RESULTS_DIR)

print("\nFiles created:")
print("- vgg16_best.keras")
print("- vgg16_final.keras")
print("- accuracy_graph.png")
print("- loss_graph.png")
print("- confusion_matrix.png")
print("- vgg16_results.txt")