
# EFFICIENTNETB0 - ORAL CANCER CLASSIFICATION
# මේ program එකෙන්:
# 1. Clean dataset එක load කරනවා
# 2. Training images සඳහා data augmentation කරනවා
# 3. EfficientNetB0 pretrained model එක load කරනවා
# 4. Transfer learning භාවිතා කරලා model එක train කරනවා
# 5. Best model එක save කරනවා
# 6. Accuracy සහ Loss graphs save කරනවා
# 7. Test dataset එකෙන්:- Accuracy, Precision, Recall, F1-score calculate කරනවා
# 8. Confusion Matrix එක save කරනවා
# 9. Model parameters save කරනවා

# IMPORTANT: EfficientNetB0 එකේ preprocessing එක model එක ඇතුළෙම තියෙන නිසා ImageDataGenerator එකෙන් 1/255 rescale කරන්නේ නැහැ.
# Original dataset එක modify කරන්නේ නැහැ.

# 1. Required libraries import කිරීම

import os
import time
import numpy as np
import matplotlib.pyplot as plt

# TensorFlow / Keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Scikit-learn
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# 2. Basic settings

DATASET_DIR = r"D:\Computer vision\clean_dataset" # Clean dataset එක තියෙන location එක
RESULTS_DIR = r"D:\FYP\training\results_efficientnet" # EfficientNet results save කරන folder එක

# EfficientNetB0 සඳහා standard input size
IMG_HEIGHT = 224
IMG_WIDTH = 224

# එක batch එකක images ගණන
BATCH_SIZE = 32

# Maximum epochs
EPOCHS = 20

# Reproducibility සඳහා random seed එක
SEED = 42

# 3. Dataset folder paths

TRAIN_DIR = os.path.join(DATASET_DIR, "training")
VAL_DIR = os.path.join(DATASET_DIR, "validation")
TEST_DIR = os.path.join(DATASET_DIR, "testing")


# Results folder එක නැත්නම් create කරනවා
os.makedirs(RESULTS_DIR, exist_ok=True)

# 4. Dataset folders check කිරීම

print("=" * 70)
print("EFFICIENTNETB0 - ORAL CANCER CLASSIFICATION")
print("=" * 70)

print("\nChecking dataset folders...")
for folder in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
    if not os.path.exists(folder):
        raise FileNotFoundError(
            f"Dataset folder not found: {folder}"
        )
print("All dataset folders found successfully.")

# 5. Data Augmentation
# Data augmentation ONLY training dataset එකට. Validation සහ testing images modify කරන්නේ නැහැ.
# EfficientNetB0 model එක ඇතුළේ preprocessing/rescaling තියෙන නිසා මෙතන rescale=1/255 දාන්නේ නැහැ.

train_datagen = ImageDataGenerator(
       rotation_range=15,  # Image එක slightly rotate කරනවා 
       width_shift_range=0.10, # Horizontal movement
       height_shift_range=0.10,     # Vertical movement
       zoom_range=0.10,   # Slight zoom   
       horizontal_flip=True # Horizontal flip
)

# 6. Validation / Testing preprocessing
# Validation සහ testing වල augmentation නැහැ.
# EfficientNetB0 model එක ඇතුළේ preprocessing handle කරන නිසා rescale එක මෙතනත් දාන්නේ නැහැ.

validation_datagen = ImageDataGenerator()
test_datagen = ImageDataGenerator()

# 7. Training dataset load කිරීම

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),   # සියලු images 224 x 224 බවට resize කරනවා
    batch_size=BATCH_SIZE,   # Batch size   
    class_mode="binary", # Binary classification  
    seed=SEED,  # Random seed
    shuffle=True  # Training data shuffle කරනවා
)

# 8. Validation dataset load කිරීම

validation_generator = validation_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    seed=SEED,
    # Validation order එක stable තියාගන්න
    shuffle=False
)

# 9. Testing dataset load කිරීම

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    seed=SEED,
    # Testing data shuffle කරන්න එපා
    shuffle=False
)
# 10. Class mapping check කිරීම

print("\n" + "=" * 70)
print("CLASS MAPPING")
print("=" * 70)

print(train_generator.class_indices)

print("\nDataset sizes:")
print("Training images   :", train_generator.samples)
print("Validation images :", validation_generator.samples)
print("Testing images    :", test_generator.samples)

# 11. Actual class indices identify කිරීම

# flow_from_directory() class names alphabetical order අනුව index assign කරනවා.
# ඒ නිසා manually 0 = cancer / 1 = not_cancer කියලා assume කරන්නේ නැහැ.

class_indices = train_generator.class_indices

# Class name අනුව actual index එක ලබාගන්නවා
cancer_index = class_indices["cancer"]
not_cancer_index = class_indices["not_cancer"]

print("\nCancer class index    :", cancer_index)
print("Not-cancer class index:", not_cancer_index)

# 12. EfficientNetB0 pretrained model

# ImageNet pretrained weights භාවිතා කරනවා.
# include_top=False: ImageNet original classification layer එක remove කරනවා.
# EfficientNetB0 internally input preprocessing handle කරන නිසා external rescale එකක් use කරන්නේ නැහැ.

print("\nLoading EfficientNetB0 pretrained model...")
base_model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
)

# 13. Base model freeze කිරීම

# මුලින් pretrained layers freeze කරනවා.
# එතකොට small medical image dataset එකෙන් pretrained features ඉක්මනින් destroy වෙන්නේ නැහැ.

base_model.trainable = False

# 14. Classification head එක build කිරීම

model = keras.Sequential([
    
    base_model, # Pretrained EfficientNetB0
    layers.GlobalAveragePooling2D(),   # Feature maps එක vector එකකට convert කරනවා
    # Overfitting අඩු කිරීමට Dropout
    layers.Dropout(0.3),
    # Binary classification සඳහා sigmoid
    layers.Dense(
        1,
        activation="sigmoid"
    )
])

# 15. Model compile කිරීම

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001
    ),

    # Binary classification
    loss="binary_crossentropy",

    metrics=["accuracy"]
)

# 16. Model summary

print("\n" + "=" * 70)
print("MODEL SUMMARY")
print("=" * 70)

model.summary()

# 17. Model parameters calculate කිරීම

total_params = model.count_params()
trainable_params = np.sum([
    np.prod(variable.shape)
    for variable in model.trainable_variables
])

non_trainable_params = total_params - trainable_params

print("\n" + "=" * 70)
print("MODEL PARAMETERS")
print("=" * 70)

print( f"Total parameters      : {total_params:,}" )
print( f"Trainable parameters  : {trainable_params:,}" )
print( f"Non-trainable params  : {non_trainable_params:,}")

# 18. Model save paths

best_model_path = os.path.join(
    RESULTS_DIR,
    "efficientnetb0_best.keras"
)

final_model_path = os.path.join(
    RESULTS_DIR,
    "efficientnetb0_final.keras"
)

# 19. ModelCheckpoint
# Validation loss හොඳම model එක save කරනවා.
checkpoint = ModelCheckpoint(

    best_model_path,

    monitor="val_loss",

    save_best_only=True,

    verbose=1
)

# 20. EarlyStopping
# Validation loss improve නොවුණොත් training unnecessarily continue කරන්නේ නැහැ.

early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# 21. Start training

print("\n" + "=" * 70)
print("STARTING EFFICIENTNETB0 TRAINING")
print("=" * 70)

start_time = time.time()

history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=EPOCHS,
    callbacks=[
        checkpoint,
        early_stopping
    ],
    verbose=1
)

# 22. Training time

end_time = time.time()
training_time = end_time - start_time
training_minutes = training_time / 60

print("\nTraining completed.")
print( f"Training Time : {training_minutes:.2f} minutes")

# 23. Final model save කිරීම

model.save(final_model_path)

print("\nFinal model saved to:")
print(final_model_path)

print("\nBest model saved to:")
print(best_model_path)

# 24. Accuracy graph

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["accuracy"],
    label="Training Accuracy"
)

plt.plot(
    history.history["val_accuracy"],
    label="Validation Accuracy"
)

plt.title(
    "EfficientNetB0 Training and Validation Accuracy"
)

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

# 25. Loss graph

plt.figure(figsize=(8, 6))

plt.plot(
    history.history["loss"],
    label="Training Loss"
)

plt.plot(
    history.history["val_loss"],
    label="Validation Loss"
)

plt.title(
    "EfficientNetB0 Training and Validation Loss"
)

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

# 26. Best model load කිරීම

best_model = keras.models.load_model(
    best_model_path
)

# 27. Test dataset evaluation

print("\n" + "=" * 70)
print("EFFICIENTNETB0 FINAL TEST EVALUATION")
print("=" * 70)

test_loss, test_accuracy = best_model.evaluate(
    test_generator,
    verbose=1
)

print( f"\nTest Loss : {test_loss:.4f}" )

print( f"Test Accuracy : {test_accuracy:.4f}" )

# 28. Test predictions generate කිරීම

test_generator.reset()
predictions = best_model.predict(
    test_generator,
    verbose=1
)

# 29. Binary predictions
# Sigmoid output:
# >= 0.5 -> class index 1
# <  0.5 -> class index 0

# Actual class names class_indices එක අනුව automatically interpret කරනවා.

y_pred = (
    predictions.ravel() >= 0.5
).astype(int)

y_true = test_generator.classes

# 30. Standard metrics
# මෙතන positive class එක "cancer" ලෙස explicitly define කරනවා. ඒ නිසා Precision / Recall / F1 කියන්නේ cancer detection performance එක.

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    pos_label=cancer_index,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    pos_label=cancer_index,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    pos_label=cancer_index,
    zero_division=0
)

# 31. Metrics print කිරීම

print("\n" + "=" * 70)
print("EFFICIENTNETB0 TEST RESULTS")
print("=" * 70)

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

# 32. Classification Report

# Actual class order automatically use කරනවා
class_names = [
    name
    for name, index in sorted(
        class_indices.items(),
        key=lambda item: item[1]
    )
]


report = classification_report(
    y_true,
    y_pred,
    labels=[0, 1],
    target_names=class_names,
    zero_division=0
)

print("\nClassification Report:")
print(report)

# 33. Confusion Matrix

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
)

print("\nConfusion Matrix:")
print(cm)

# 34. Confusion Matrix graph

plt.figure(figsize=(7, 6))
plt.imshow(cm)
plt.title( "EfficientNetB0 Confusion Matrix")
plt.xlabel( "Predicted Label")
plt.ylabel( "True Label" )
plt.xticks(
    [0, 1],
    class_names
)
plt.yticks(
    [0, 1],
    class_names
)

# Confusion matrix values display කරනවා
for i in range(2):
    for j in range(2):
        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )

plt.colorbar()
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

# 35. Results text file

results_file = os.path.join(
    RESULTS_DIR,
    "efficientnetb0_results.txt"
)

with open(
    results_file,
    "w",
    encoding="utf-8"

) as file:
    file.write(
        "EFFICIENTNETB0 - ORAL CANCER CLASSIFICATION RESULTS\n"
    )
    file.write("=" * 70 + "\n\n")

    # Dataset information
    file.write("DATASET INFORMATION\n")

    file.write("-" * 70 + "\n")

    file.write( f"Training images  : {train_generator.samples}\n"  )
    file.write( f"Validation images : {validation_generator.samples}\n" )
    file.write( f"Testing images    : {test_generator.samples}\n" )
    file.write(  f"Input size        : {IMG_HEIGHT} x {IMG_WIDTH}\n"  )
    file.write(  f"Batch size        : {BATCH_SIZE}\n"  )
    file.write(  f"Maximum epochs    : {EPOCHS}\n" )
    file.write( f"Training time     : {training_minutes:.2f} minutes\n\n" )

    # Class mapping
    file.write("CLASS MAPPING\n")

    file.write("-" * 70 + "\n")

    file.write(
        f"{class_indices}\n\n"
    )


    # Parameter information
    file.write("MODEL PARAMETERS\n")

    file.write("-" * 70 + "\n")

    file.write(
        f"Total parameters     : {total_params:,}\n"
    )

    file.write(
        f"Trainable parameters : {trainable_params:,}\n"
    )

    file.write(
        f"Non-trainable params : {non_trainable_params:,}\n\n"
    )


    # Test results
    file.write("TEST RESULTS\n")

    file.write("-" * 70 + "\n")

    file.write(
        f"Test Loss     : {test_loss:.4f}\n"
    )

    file.write(
        f"Accuracy      : {accuracy:.4f} "
        f"({accuracy * 100:.2f}%)\n"
    )

    file.write(
        f"Precision     : {precision:.4f} "
        f"({precision * 100:.2f}%)\n"
    )

    file.write(
        f"Recall        : {recall:.4f} "
        f"({recall * 100:.2f}%)\n"
    )

    file.write(
        f"F1-score      : {f1:.4f} "
        f"({f1 * 100:.2f}%)\n\n"
    )


    # Classification report
    file.write("CLASSIFICATION REPORT\n")

    file.write("-" * 70 + "\n")

    file.write(report)


    # Confusion matrix
    file.write(
        "\n\nCONFUSION MATRIX\n"
    )

    file.write("-" * 70 + "\n")

    file.write(
        str(cm)
    )


# ------------------------------------------------
# 36. Final output
# ------------------------------------------------

print("\n" + "=" * 70)

print(
    "EFFICIENTNETB0 PROCESS COMPLETED SUCCESSFULLY"
)

print("=" * 70)


print("\nResults saved in:")

print(RESULTS_DIR)


print("\nGenerated files:")

print("1. efficientnetb0_best.keras")

print("2. efficientnetb0_final.keras")

print("3. accuracy_graph.png")

print("4. loss_graph.png")

print("5. confusion_matrix.png")

print("6. efficientnetb0_results.txt")


print("\n" + "=" * 70)