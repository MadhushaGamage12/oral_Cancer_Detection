# ================================================================
# RESNET50 - ORAL CANCER CLASSIFICATION
# ================================================================
#
# මේ script එකෙන්:
# 1. Clean dataset එකෙන් images load කරනවා
# 2. ResNet50 model එක train කරනවා
# 3. Validation data භාවිතා කරලා best model එක save කරනවා
# 4. Test dataset එකෙන් final evaluation කරනවා
# 5. Accuracy, Precision, Recall, F1-score ගණනය කරනවා
# 6. Confusion Matrix එක generate කරනවා
# 7. Accuracy සහ Loss graphs save කරනවා
# 8. සියලුම results text file එකකට save කරනවා
#
# Existing models:
# Baseline CNN
# MobileNetV2
# EfficientNetB0
#
# මේ model එක ඒවාට වෙනම train වෙනවා.
# ================================================================

# 1. LIBRARIES IMPORT කිරීම

import os
import time
import numpy as np
import matplotlib.pyplot as plt

# TensorFlow සහ Keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import ResNet50

# Model evaluation සඳහා
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# 2. BASIC SETTINGS

# Clean dataset  location 
DATASET_PATH = r"D:\Computer vision\clean_dataset"

# ResNet50 input image size 224 x 224 
IMG_SIZE = (224, 224)

BATCH_SIZE = 32 # එකවර model එකට images කීයක් යවනවද

EPOCHS = 20 # Maximum training epochs

SEED = 42 # Random seed එකක් දාන්නේ results reproducibility එකට

# 3. RESULT FOLDER එක CREATE කිරීම
# ResNet50 results වෙනම folder එකක save කරනවා.
# මේකෙන් කලින් models වල results overwrite වෙන්නේ නැහැ.

RESULTS_PATH = r"D:\FYP\training\results_resnet50"

os.makedirs(RESULTS_PATH, exist_ok=True)

# 4. MODEL FILE PATHS

# Best validation performance තිබුණු model එක
BEST_MODEL_PATH = os.path.join(
    RESULTS_PATH,
    "resnet50_best.keras"
)

# Training අවසානයේ save කරන final model එක
FINAL_MODEL_PATH = os.path.join(
    RESULTS_PATH,
    "resnet50_final.keras"
)

# 5. GRAPH / RESULT FILE PATHS
ACCURACY_GRAPH_PATH = os.path.join(
    RESULTS_PATH,
    "accuracy_graph.png"
)

LOSS_GRAPH_PATH = os.path.join(
    RESULTS_PATH,
    "loss_graph.png"
)

CONFUSION_MATRIX_PATH = os.path.join(
    RESULTS_PATH,
    "confusion_matrix.png"
)

RESULTS_TEXT_PATH = os.path.join(
    RESULTS_PATH,
    "resnet50_results.txt"
)


# 6. DATASET PATHS
TRAIN_PATH = os.path.join(DATASET_PATH, "training")
VAL_PATH = os.path.join(DATASET_PATH, "validation")
TEST_PATH = os.path.join(DATASET_PATH, "testing")

# 7. CHECK DATASET PATHS

print("\n" + "=" * 70)
print("RESNET50 ORAL CANCER TRAINING")
print("=" * 70)

print("\nChecking dataset paths...")

if not os.path.exists(TRAIN_PATH):
    raise FileNotFoundError(
        f"Training folder not found:\n{TRAIN_PATH}"
    )

if not os.path.exists(VAL_PATH):
    raise FileNotFoundError(
        f"Validation folder not found:\n{VAL_PATH}"
    )

if not os.path.exists(TEST_PATH):
    raise FileNotFoundError(
        f"Testing folder not found:\n{TEST_PATH}"
    )

print("Dataset paths found successfully.")

# 8. LOAD TRAINING DATA

print("\nLoading training dataset...")

train_dataset = tf.keras.utils.image_dataset_from_directory(
    TRAIN_PATH,

    # Images 224 x 224 වලට resize කරනවා
    image_size=IMG_SIZE,

    # Batch size
    batch_size=BATCH_SIZE,

    # Classes automatically folders වලින් identify කරනවා
    # cancer
    # not_cancer
    label_mode="binary",
    shuffle=True,
    seed=SEED
)

# 9. LOAD VALIDATION DATA

print("\nLoading validation dataset...")
validation_dataset = tf.keras.utils.image_dataset_from_directory(
    VAL_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    # Validation data shuffle නොකරන එක evaluation එකට convenient
    shuffle=False
)

# 10. LOAD TEST DATA

print("\nLoading testing dataset...")
test_dataset = tf.keras.utils.image_dataset_from_directory(
    TEST_PATH,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="binary",
    # Test data shuffle නොකරනවා.
    # එතකොට predictions සහ true labels match කරගන්න ලේසි.
    shuffle=False
)

# 11. CLASS NAMES CHECK කිරීම
class_names = train_dataset.class_names

print("\nClass names:")
print(class_names)

# 12. DATA PERFORMANCE OPTIMIZATION
# AUTOTUNE කියන්නේ TensorFlow එකට data loading
# automatically optimize කරන්න දෙන setting එක.

AUTOTUNE = tf.data.AUTOTUNE
train_dataset = train_dataset.prefetch(
    buffer_size=AUTOTUNE
)

validation_dataset = validation_dataset.prefetch(
    buffer_size=AUTOTUNE
)

test_dataset = test_dataset.prefetch(
    buffer_size=AUTOTUNE
)

# 13. DATA AUGMENTATION
# මෙතන augmentation use කරන්නේ training images වලට විතරයි.
## Validation සහ testing images වලට augmentation apply කරන්නේ නැහැ.
# Data size relatively small නිසා model එකට slightly different training examples ලබාදෙන්නaugmentation use කරනවා.


data_augmentation = keras.Sequential(
    [

        # Random horizontal flip
        layers.RandomFlip("horizontal"),

        # Small rotation
        layers.RandomRotation(0.10),

        # Small zoom
        layers.RandomZoom(0.10),

    ],
    name="data_augmentation"
)


# 14. RESNET50 BASE MODEL
# ResNet50 එක ImageNet pretrained weights සමඟ load කරනවා.
# include_top=False කියන්නේ original ImageNet classifier
# remove කරලා අපේ cancer/not_cancer classification
# task එකට custom classifier එකක් දානවා.

base_model = ResNet50(
    weights="imagenet",

    # Original 1000-class classification layer remove කරනවා
    include_top=False,

    # අපේ input size
    input_shape=(224, 224, 3)
)

# 15. BASE MODEL FREEZE කිරීම
# මුලින් pretrained ResNet50 layers freeze කරනවා.
# එතකොට ImageNet වලින් already learn කරපු
# low-level features preserve වෙනවා.

base_model.trainable = False

# 16. BUILD FULL RESNET50 MODEL

inputs = keras.Input(
    shape=(224, 224, 3)
)

x = data_augmentation(inputs) # Data augmentation apply කිරීම

# ResNet50 preprocessing ResNet50 ImageNet pretrained model එක නිසා ResNet50 specific preprocessing function එක use කරනවා.
x = tf.keras.applications.resnet50.preprocess_input(x)

# Pretrained ResNet50 feature extractor

x = base_model(
    x,
    training=False
)

# 17. GLOBAL AVERAGE POOLING Feature maps එක small vector එකකට convert කරනවා.

x = layers.GlobalAveragePooling2D()(x)

# 18. DROPOUT Overfitting reduce කරන්න dropout use කරනවා.

x = layers.Dropout(0.3)(x)

# 19. FINAL CLASSIFICATION LAYER
# Binary classification:
# 0 = not_cancer
# 1 = cancer

# sigmoid activation එකෙන් probability එකක් ලබාගන්නවා.

outputs = layers.Dense(
    1,
    activation="sigmoid"
)(x)


# 20. FINAL MODEL CREATE කිරීම

model = keras.Model(
    inputs=inputs,
    outputs=outputs,
    name="ResNet50_Oral_Cancer"
)

# 21. MODEL SUMMARY

print("\n" + "=" * 70)
print("RESNET50 MODEL SUMMARY")
print("=" * 70)

model.summary()

# 22. COMPILE MODEL

model.compile(

    # Adam optimizer
    optimizer=keras.optimizers.Adam(
        learning_rate=0.0001
    ),

    # Binary classification loss
    loss="binary_crossentropy",

    # Accuracy metric
    metrics=["accuracy"]
)


# 23. CALLBACKS

# ModelCheckpoint Validation loss අඩුම model එක save කරනවා. ඒ නිසා training අවසානයේ last epoch model එක වෙනුවට best model එක අපිට ලබාගන්න පුළුවන්.

checkpoint = keras.callbacks.ModelCheckpoint(
    BEST_MODEL_PATH,
    monitor="val_loss",
    save_best_only=True,
    mode="min",
    verbose=1
)


# EarlyStopping Validation loss improve නොවුනොත් training unnecessary ලෙස continue නොකර නවත්වනවා.patience=5 කියන්නේ epochs 5ක් improvement නැත්නම් stop.

early_stopping = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# 24. START TRAINING

print("\n" + "=" * 70)
print("STARTING RESNET50 TRAINING")
print("=" * 70)

# Training start time
start_time = time.time()

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS,
    callbacks=[
        checkpoint,
        early_stopping
    ]
)

# 25. TRAINING TIME

end_time = time.time()
training_time_seconds = end_time - start_time
training_time_minutes = training_time_seconds / 60
print("\n" + "=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print(
    f"Training Time : "
    f"{training_time_minutes:.2f} minutes"
)

# 26. SAVE FINAL MODEL

model.save(FINAL_MODEL_PATH)

print("\nFinal model saved to:")
print(FINAL_MODEL_PATH)

print("\nBest model saved to:")
print(BEST_MODEL_PATH)

# 27. PLOT ACCURACY GRAPH

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["accuracy"],
    label="Training Accuracy"
)

plt.plot(
    history.history["val_accuracy"],
    label="Validation Accuracy"
)

plt.title("ResNet50 Training and Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)
plt.savefig(
    ACCURACY_GRAPH_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 28. PLOT LOSS GRAPH

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["loss"],
    label="Training Loss"
)

plt.plot(
    history.history["val_loss"],
    label="Validation Loss"
)

plt.title("ResNet50 Training and Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)
plt.savefig(
    LOSS_GRAPH_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()



# 29. LOAD BEST MODEL Test evaluation සඳහා best validation model එක use කරනවා.

print("\nLoading best ResNet50 model...")
best_model = keras.models.load_model(
    BEST_MODEL_PATH
)


# 30. TEST DATA EVALUATION

print("\n" + "=" * 70)
print("RESNET50 TEST EVALUATION")
print("=" * 70)

test_loss, test_accuracy = best_model.evaluate(
    test_dataset,
    verbose=1
)

# 31. GET PREDICTIONS Test images වල predicted probabilities ලබාගන්නවා.

predictions = best_model.predict(
    test_dataset,
    verbose=1
)

# 32. CONVERT PROBABILITY TO CLASS : Probability >= 0.5 නම් class 1 ,  Probability < 0.5 නම් class 0
# class 0 = not_cancer
# class 1 = cancer

y_pred = (
    predictions.ravel() >= 0.5
).astype(int)


# 33. GET TRUE LABELS

y_true = np.concatenate(
    [
        labels.numpy()
        for images, labels in test_dataset
    ]
).astype(int)

# 34. CALCULATE PERFORMANCE METRICS

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

# 35. CLASSIFICATION REPORT

classification_rep = classification_report(
    y_true,
    y_pred,
    target_names=class_names,
    zero_division=0
)

# 36. CONFUSION MATRIX

cm = confusion_matrix(
    y_true,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)

# 37. PLOT CONFUSION MATRIX

plt.figure(figsize=(7, 6))

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title("ResNet50 Confusion Matrix")
plt.colorbar()
plt.xticks(
    np.arange(len(class_names)),
    class_names,
    rotation=45
)

plt.yticks(
    np.arange(len(class_names)),
    class_names
)

plt.xlabel("Predicted Label")
plt.ylabel("True Label")

# Confusion matrix එකේ values display කරනවා

for i in range(cm.shape[0]):

    for j in range(cm.shape[1]):

        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )


plt.tight_layout()

plt.savefig(
    CONFUSION_MATRIX_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 38. PRINT FINAL RESULTS

print("\n" + "=" * 70)
print("RESNET50 FINAL TEST RESULTS")
print("=" * 70)

print(
    f"\nTest Loss     : {test_loss:.4f}"
)

print(
    f"Test Accuracy : {test_accuracy:.4f}"
)

print(
    f"\nAccuracy  : {accuracy:.4f} "
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

print("\nClassification Report:")
print(classification_rep)

print("Confusion Matrix:")
print(cm)


# 39. SAVE ALL RESULTS TO TEXT FILE

with open(
    RESULTS_TEXT_PATH,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "# RESNET50 TEST RESULTS\n\n"
    )

    f.write(
        f"Training Time : "
        f"{training_time_minutes:.2f} minutes\n\n"
    )

    f.write(
        f"Test Loss     : "
        f"{test_loss:.4f}\n"
    )

    f.write(
        f"Test Accuracy : "
        f"{test_accuracy:.4f}\n\n"
    )

    f.write(
        f"Accuracy  : "
        f"{accuracy:.4f} "
        f"({accuracy * 100:.2f}%)\n"
    )

    f.write(
        f"Precision : "
        f"{precision:.4f} "
        f"({precision * 100:.2f}%)\n"
    )

    f.write(
        f"Recall    : "
        f"{recall:.4f} "
        f"({recall * 100:.2f}%)\n"
    )

    f.write(
        f"F1-score  : "
        f"{f1:.4f} "
        f"({f1 * 100:.2f}%)\n\n"
    )

    f.write(
        "Classification Report:\n"
    )

    f.write(
        classification_rep
    )

    f.write(
        "\nConfusion Matrix:\n"
    )

    f.write(
        str(cm)
    )

# 40. FINAL OUTPUT

print("\n" + "=" * 70)
print("RESULTS SAVED")
print("=" * 70)

print("\nResults saved in:")
print(RESULTS_PATH)

print("\nGenerated files:")

print("1. resnet50_best.keras")
print("2. resnet50_final.keras")
print("3. accuracy_graph.png")
print("4. loss_graph.png")
print("5. confusion_matrix.png")
print("6. resnet50_results.txt")

print("\n" + "=" * 70)
print("RESNET50 PROCESS COMPLETED SUCCESSFULLY")
print("=" * 70)