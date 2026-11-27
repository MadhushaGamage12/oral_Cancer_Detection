# ============================================================
# MOBILENETV2 - ORAL CANCER IMAGE CLASSIFICATION
# ============================================================
#
# Project:
# Oral Cancer Detection Using Deep Learning
#
# Purpose:
# This script trains a MobileNetV2 model for oral cancer
# classification.
#
# The MobileNetV2 result will be compared with the
# Baseline CNN model.
#
# Dataset:
# D:\Computer vision\clean_dataset
#
# Classes:
#   0 = cancer
#   1 = not_cancer
#
# This script performs:
#   1. Load the clean dataset
#   2. Preprocess images
#   3. Apply data augmentation to training images
#   4. Load MobileNetV2 with ImageNet weights
#   5. Add a custom classification layer
#   6. Train the model
#   7. Save the best model
#   8. Evaluate the model on the test set
#   9. Calculate Accuracy, Precision, Recall and F1-score
#  10. Generate a Confusion Matrix
#  11. Generate Accuracy and Loss graphs
#
# ============================================================


# ============================================================
# 1. IMPORT REQUIRED LIBRARIES
# ============================================================

# Used for creating folders and handling file paths.
import os

# NumPy is used for numerical operations.
import numpy as np

# TensorFlow is the main deep learning framework.
import tensorflow as tf

# Keras is included inside TensorFlow.
from tensorflow import keras

# Sequential is used to create the final classification model.
from tensorflow.keras import Sequential

# Required Keras layers.
from tensorflow.keras import layers

# Used to load images from folder structures.
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# MobileNetV2 is a lightweight CNN architecture.
from tensorflow.keras.applications import MobileNetV2

# These metrics are used for final model evaluation.
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Matplotlib is used to create graphs.
import matplotlib.pyplot as plt


# ============================================================
# 2. BASIC CONFIGURATION
# ============================================================

# Path to the CLEAN dataset.
#
# IMPORTANT:
# We use exactly the same clean dataset that was used
# for the Baseline CNN.
DATASET_DIR = r"D:\Computer vision\clean_dataset"

# MobileNetV2 normally uses 224 x 224 images.
IMG_HEIGHT = 224
IMG_WIDTH = 224

# Number of images processed at one time.
BATCH_SIZE = 32

# Maximum number of training epochs.
EPOCHS = 20

# Random seed helps make the experiment reproducible.
SEED = 42

# Create a separate folder for MobileNet results.
#
# This folder will be created automatically.
RESULTS_DIR = r"D:\FYP\training\results_mobilenet"

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ============================================================
# 3. DISPLAY TENSORFLOW INFORMATION
# ============================================================

print("=" * 70)
print("MOBILENETV2 - ORAL CANCER CLASSIFICATION")
print("=" * 70)

print(
    f"TensorFlow version: {tf.__version__}"
)


# Check whether a GPU is available.
gpus = tf.config.list_physical_devices("GPU")

if gpus:

    print("GPU detected.")
    print(gpus)

else:

    print(
        "GPU not detected. Training will use CPU."
    )


# ============================================================
# 4. DEFINE DATASET PATHS
# ============================================================

# Training images.
TRAIN_DIR = os.path.join(
    DATASET_DIR,
    "training"
)

# Validation images.
VALIDATION_DIR = os.path.join(
    DATASET_DIR,
    "validation"
)

# Testing images.
TEST_DIR = os.path.join(
    DATASET_DIR,
    "testing"
)


# ============================================================
# 5. CHECK THAT DATASET FOLDERS EXIST
# ============================================================

print()
print("=" * 70)
print("CHECKING DATASET")
print("=" * 70)


if not os.path.exists(TRAIN_DIR):

    raise FileNotFoundError(
        f"Training folder not found: {TRAIN_DIR}"
    )


if not os.path.exists(VALIDATION_DIR):

    raise FileNotFoundError(
        f"Validation folder not found: {VALIDATION_DIR}"
    )


if not os.path.exists(TEST_DIR):

    raise FileNotFoundError(
        f"Testing folder not found: {TEST_DIR}"
    )


print(
    f"Training folder   : {TRAIN_DIR}"
)

print(
    f"Validation folder : {VALIDATION_DIR}"
)

print(
    f"Testing folder    : {TEST_DIR}"
)

print(
    "Dataset folders found successfully."
)


# ============================================================
# 6. IMAGE PREPROCESSING AND DATA AUGMENTATION
# ============================================================

# Training images receive augmentation.
#
# This creates slightly different versions of training
# images and helps the model generalize better.
#
# rescale:
# Converts pixel values from 0-255 to approximately 0-1.
#
# rotation_range:
# Slightly rotates images.
#
# width_shift_range:
# Moves images horizontally.
#
# height_shift_range:
# Moves images vertically.
#
# zoom_range:
# Slightly zooms images.
#
# horizontal_flip:
# Randomly flips images horizontally.
#
# IMPORTANT:
# Augmentation is applied ONLY to training images.

training_datagen = ImageDataGenerator(

    rescale=1.0 / 255.0,

    rotation_range=15,

    width_shift_range=0.10,

    height_shift_range=0.10,

    zoom_range=0.10,

    horizontal_flip=True
)


# Validation images are NOT augmented.
#
# Only normalization is applied.
validation_datagen = ImageDataGenerator(

    rescale=1.0 / 255.0
)


# Testing images are NOT augmented.
#
# The test set must represent unseen real images.
test_datagen = ImageDataGenerator(

    rescale=1.0 / 255.0
)


# ============================================================
# 7. LOAD TRAINING DATA
# ============================================================

print()
print("=" * 70)
print("LOADING TRAINING DATA")
print("=" * 70)


train_generator = training_datagen.flow_from_directory(

    TRAIN_DIR,

    # Resize all images to 224 x 224.
    target_size=(
        IMG_HEIGHT,
        IMG_WIDTH
    ),

    # Process 32 images at a time.
    batch_size=BATCH_SIZE,

    # Binary classification because there are two classes.
    class_mode="binary",

    # Shuffle training images.
    shuffle=True,

    # Reproducibility.
    seed=SEED
)


# ============================================================
# 8. LOAD VALIDATION DATA
# ============================================================

print()
print("=" * 70)
print("LOADING VALIDATION DATA")
print("=" * 70)


validation_generator = validation_datagen.flow_from_directory(

    VALIDATION_DIR,

    target_size=(
        IMG_HEIGHT,
        IMG_WIDTH
    ),

    batch_size=BATCH_SIZE,

    class_mode="binary",

    # Keep validation order fixed.
    shuffle=False
)


# ============================================================
# 9. LOAD TEST DATA
# ============================================================

print()
print("=" * 70)
print("LOADING TEST DATA")
print("=" * 70)


test_generator = test_datagen.flow_from_directory(

    TEST_DIR,

    target_size=(
        IMG_HEIGHT,
        IMG_WIDTH
    ),

    batch_size=BATCH_SIZE,

    class_mode="binary",

    # IMPORTANT:
    # Test images must remain in a fixed order.
    #
    # This is necessary when calculating the
    # confusion matrix and sklearn metrics.
    shuffle=False
)


# ============================================================
# 10. DISPLAY CLASS INFORMATION
# ============================================================

print()
print("=" * 70)
print("CLASS LABELS")
print("=" * 70)


print(
    train_generator.class_indices
)


# Expected output should be:
#
# {'cancer': 0, 'not_cancer': 1}
#
# The dictionary tells us which numerical label
# belongs to each class.


# ============================================================
# 11. DISPLAY DATASET COUNTS
# ============================================================

print()
print("=" * 70)
print("DATASET COUNTS")
print("=" * 70)


print(
    f"Training images   : {train_generator.samples}"
)

print(
    f"Validation images : {validation_generator.samples}"
)

print(
    f"Testing images    : {test_generator.samples}"
)


# ============================================================
# 12. LOAD MOBILE-NET-V2 BASE MODEL
# ============================================================

print()
print("=" * 70)
print("LOADING MOBILENETV2")
print("=" * 70)


# MobileNetV2 is a lightweight CNN architecture.
#
# weights="imagenet":
# Uses weights that were previously learned from
# the ImageNet dataset.
#
# include_top=False:
# Removes MobileNetV2's original classification layer.
#
# This allows us to add our own classification layer
# for the two oral cancer classes.

base_model = MobileNetV2(

    weights="imagenet",

    include_top=False,

    input_shape=(
        IMG_HEIGHT,
        IMG_WIDTH,
        3
    )
)


# ============================================================
# 13. FREEZE MOBILENETV2 BASE
# ============================================================

# Initially, we freeze the MobileNetV2 layers.
#
# This means the pre-trained feature extraction layers
# will not be changed during the first training stage.
#
# The model will only learn our new classification layers.

base_model.trainable = False


# ============================================================
# 14. BUILD THE MOBILENETV2 CLASSIFICATION MODEL
# ============================================================

print()
print("=" * 70)
print("BUILDING MOBILENETV2 MODEL")
print("=" * 70)


model = Sequential([

    # Pre-trained MobileNetV2 feature extractor.
    base_model,

    # Converts the feature maps into a single vector.
    #
    # GlobalAveragePooling2D is more lightweight than
    # Flatten because it greatly reduces the number
    # of trainable parameters.
    layers.GlobalAveragePooling2D(),

    # Dropout helps reduce overfitting.
    layers.Dropout(0.30),

    # Final binary classification layer.
    #
    # Sigmoid produces a probability between 0 and 1.
    layers.Dense(
        1,
        activation="sigmoid"
    )
])


# ============================================================
# 15. DISPLAY MODEL ARCHITECTURE
# ============================================================

print()
print("=" * 70)
print("MOBILENETV2 MODEL ARCHITECTURE")
print("=" * 70)


model.summary()


# ============================================================
# 16. COMPILE THE MODEL
# ============================================================

# Adam is the optimizer used to update model parameters.
#
# Binary crossentropy is suitable for two-class classification.
#
# Accuracy is used as a basic training metric.

model.compile(

    optimizer="adam",

    loss="binary_crossentropy",

    metrics=[
        "accuracy"
    ]
)


# ============================================================
# 17. DEFINE MODEL CHECKPOINT
# ============================================================

# Save the model whenever validation loss improves.
#
# This ensures that we keep the best-performing model
# rather than simply using the final epoch.

checkpoint_path = os.path.join(

    RESULTS_DIR,

    "mobilenet_best.keras"
)


checkpoint = keras.callbacks.ModelCheckpoint(

    checkpoint_path,

    monitor="val_loss",

    save_best_only=True,

    mode="min",

    verbose=1
)


# ============================================================
# 18. DEFINE EARLY STOPPING
# ============================================================

# Stop training if validation loss does not improve
# for several consecutive epochs.
#
# restore_best_weights=True:
# Restores the best model weights after training.

early_stopping = keras.callbacks.EarlyStopping(

    monitor="val_loss",

    patience=5,

    restore_best_weights=True,

    verbose=1
)


# ============================================================
# 19. TRAIN MOBILENETV2
# ============================================================

print()
print("=" * 70)
print("STARTING MOBILENETV2 TRAINING")
print("=" * 70)


history = model.fit(

    train_generator,

    # Validation data is used to monitor generalization.
    validation_data=validation_generator,

    # Maximum number of epochs.
    epochs=EPOCHS,

    # Save the best model and stop if necessary.
    callbacks=[
        checkpoint,
        early_stopping
    ]
)


# ============================================================
# 20. SAVE FINAL MOBILENET MODEL
# ============================================================

final_model_path = os.path.join(

    RESULTS_DIR,

    "mobilenet_final.keras"
)


model.save(
    final_model_path
)


print()
print(
    "Final model saved to:"
)

print(
    final_model_path
)


print()
print(
    "Best model saved to:"
)

print(
    checkpoint_path
)


# ============================================================
# 21. PLOT TRAINING AND VALIDATION ACCURACY
# ============================================================

plt.figure(
    figsize=(8, 6)
)


plt.plot(

    history.history["accuracy"],

    label="Training Accuracy"
)


plt.plot(

    history.history["val_accuracy"],

    label="Validation Accuracy"
)


plt.title(
    "MobileNetV2 - Training and Validation Accuracy"
)


plt.xlabel(
    "Epoch"
)


plt.ylabel(
    "Accuracy"
)


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


# ============================================================
# 22. PLOT TRAINING AND VALIDATION LOSS
# ============================================================

plt.figure(
    figsize=(8, 6)
)


plt.plot(

    history.history["loss"],

    label="Training Loss"
)


plt.plot(

    history.history["val_loss"],

    label="Validation Loss"
)


plt.title(
    "MobileNetV2 - Training and Validation Loss"
)


plt.xlabel(
    "Epoch"
)


plt.ylabel(
    "Loss"
)


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


# ============================================================
# 23. EVALUATE MOBILENETV2 ON TEST DATA
# ============================================================

print()
print("=" * 70)
print("EVALUATING MOBILENETV2 ON TEST DATA")
print("=" * 70)


# Evaluate using the completely unseen test dataset.
test_loss, test_accuracy = model.evaluate(

    test_generator,

    verbose=1
)


print()

print(
    f"Test Loss     : {test_loss:.4f}"
)

print(
    f"Test Accuracy : {test_accuracy:.4f}"
)


# ============================================================
# 24. GENERATE TEST PREDICTIONS
# ============================================================

# Reset the test generator before prediction.
#
# This ensures predictions start from the first test image.
test_generator.reset()


# Generate probability predictions.
predicted_probabilities = model.predict(

    test_generator,

    verbose=1
)


# Convert probabilities into class labels.
#
# Probability >= 0.5:
#     predicted class = 1
#
# Probability < 0.5:
#     predicted class = 0

predicted_classes = (

    predicted_probabilities >= 0.5

).astype(int).flatten()


# ============================================================
# 25. GET TRUE TEST LABELS
# ============================================================

true_classes = test_generator.classes


# ============================================================
# 26. CALCULATE PERFORMANCE METRICS
# ============================================================

# Accuracy:
# Percentage of all test images classified correctly.

accuracy = accuracy_score(

    true_classes,

    predicted_classes
)


# Precision:
# Of the images predicted as positive,
# how many were actually positive?

precision = precision_score(

    true_classes,

    predicted_classes,

    zero_division=0
)


# Recall:
# Of all actual positive images,
# how many were correctly detected?

recall = recall_score(

    true_classes,

    predicted_classes,

    zero_division=0
)


# F1-score:
# Harmonic mean of precision and recall.

f1 = f1_score(

    true_classes,

    predicted_classes,

    zero_division=0
)


# ============================================================
# 27. DISPLAY FINAL METRICS
# ============================================================

print()
print("=" * 70)
print("MOBILENETV2 FINAL TEST RESULTS")
print("=" * 70)


print(

    f"Accuracy  : {accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"

)


print(

    f"Precision : {precision:.4f} "
    f"({precision * 100:.2f}%)"

)


print(

    f"Recall    : {recall:.4f} "
    f"({recall * 100:.2f}%)"

)


print(

    f"F1-score  : {f1:.4f} "
    f"({f1 * 100:.2f}%)"

)


# ============================================================
# 28. CLASSIFICATION REPORT
# ============================================================

print()
print("=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)


# Get class names from the dataset.
class_names = list(

    test_generator.class_indices.keys()

)


print(

    classification_report(

        true_classes,

        predicted_classes,

        target_names=class_names,

        zero_division=0

    )

)


# ============================================================
# 29. CREATE CONFUSION MATRIX
# ============================================================

# The confusion matrix shows how many images were:
#
# Correctly classified
# Incorrectly classified
#
# for each class.

cm = confusion_matrix(

    true_classes,

    predicted_classes

)


print()
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)


print(cm)


# ============================================================
# 30. SAVE CONFUSION MATRIX AS IMAGE
# ============================================================

plt.figure(
    figsize=(7, 6)
)


plt.imshow(

    cm,

    interpolation="nearest"
)


plt.title(

    "MobileNetV2 - Confusion Matrix"

)


plt.colorbar()


tick_marks = np.arange(

    len(class_names)

)


plt.xticks(

    tick_marks,

    class_names,

    rotation=45

)


plt.yticks(

    tick_marks,

    class_names

)


plt.xlabel(

    "Predicted Label"

)


plt.ylabel(

    "True Label"

)


# Display the number of images inside each
# confusion matrix cell.

for i in range(cm.shape[0]):

    for j in range(cm.shape[1]):

        plt.text(

            j,

            i,

            cm[i, j],

            horizontalalignment="center"

        )


plt.tight_layout()


confusion_matrix_path = os.path.join(

    RESULTS_DIR,

    "confusion_matrix.png"

)


plt.savefig(

    confusion_matrix_path,

    dpi=300,

    bbox_inches="tight"

)


plt.close()


# ============================================================
# 31. SAVE RESULTS TO TEXT FILE
# ============================================================

results_file = os.path.join(

    RESULTS_DIR,

    "mobilenet_results.txt"

)


with open(

    results_file,

    "w",

    encoding="utf-8"

) as file:

    file.write(
        "MOBILENETV2 TEST RESULTS\n"
    )

    file.write(
        "========================\n\n"
    )

    file.write(
        f"Test Loss: {test_loss:.4f}\n"
    )

    file.write(
        f"Accuracy: {accuracy:.4f}\n"
    )

    file.write(
        f"Precision: {precision:.4f}\n"
    )

    file.write(
        f"Recall: {recall:.4f}\n"
    )

    file.write(
        f"F1-score: {f1:.4f}\n\n"
    )

    file.write(
        "Confusion Matrix:\n"
    )

    file.write(
        str(cm)
    )


# ============================================================
# 32. FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("MOBILENETV2 TRAINING COMPLETED")
print("=" * 70)


print()
print(
    "Results saved in:"
)

print(
    RESULTS_DIR
)


print()
print(
    "Generated files:"
)


print(
    "1. mobilenet_best.keras"
)

print(
    "2. mobilenet_final.keras"
)

print(
    "3. accuracy_graph.png"
)

print(
    "4. loss_graph.png"
)

print(
    "5. confusion_matrix.png"
)

print(
    "6. mobilenet_results.txt"
)


print()
print("=" * 70)
print("MOBILENETV2 PROCESS COMPLETED SUCCESSFULLY")
print("=" * 70)