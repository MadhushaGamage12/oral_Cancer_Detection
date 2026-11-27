# BASELINE CNN - ORAL CANCER IMAGE CLASSIFICATION

# Purpose:
# This script trains a simple CNN model as the baseline model.
# The baseline CNN will later be compared with MobileNet.

# Classes:
#   0 = cancer
#   1 = not_cancer

# The script performs:
#   1. Load the dataset
#   2. Preprocess the images
#   3. Apply data augmentation to training images
#   4. Build a baseline CNN
#   5. Train the model
#   6. Save the best model
#   7. Evaluate the model on the test set
#   8. Calculate Accuracy, Precision, Recall and F1-score
#   9. Generate a Confusion Matrix
#  10. Generate Accuracy and Loss graphs

# 1. IMPORT REQUIRED LIBRARIES

import os # Operating system functions are used for creating folders and handling file paths.
import numpy as np # NumPy is used for numerical calculations.
import tensorflow as tf # TensorFlow is the main deep learning framework used to build and train the CNN model.
from tensorflow import keras # Keras is included inside TensorFlow and provides tools for creating neural network models.
from tensorflow.keras import Sequential  # Sequential allows us to build the CNN layer by layer.
from tensorflow.keras import layers # CNN layers used to construct the baseline model.
from tensorflow.keras.preprocessing.image import ImageDataGenerator # ImageDataGenerator is used to load images from folders and apply data augmentation to the training images.

# Classification metrics are used to evaluate the model.
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Matplotlib is used to create graphs and the confusion matrix.
import matplotlib.pyplot as plt

# 2. BASIC CONFIGURATION

DATASET_DIR = r"D:\Computer vision\clean_dataset"  # Path to the cleaned dataset.This dataset was created after removing exact duplicates.

# Image dimensions. All images will be resized to 224 x 224 pixels.
IMG_HEIGHT = 224
IMG_WIDTH = 224

BATCH_SIZE = 32 # Number of images processed at one time.
EPOCHS = 20 # Number of complete passes through the training dataset.
SEED = 42 # Random seed makes the experiment more reproducible.

RESULTS_DIR = r"D:\FYP\training\results_baseline" # Create a folder to store model results.
os.makedirs(RESULTS_DIR, exist_ok=True)

# 3. DISPLAY TENSORFLOW VERSION

print("=" * 70)
print("BASELINE CNN - ORAL CANCER CLASSIFICATION")
print("=" * 70)
print(f"TensorFlow version: {tf.__version__}")

gpus = tf.config.list_physical_devices("GPU") # Display whether TensorFlow can detect a GPU.

if gpus:
    print("GPU detected.")
    print(gpus)
else:
    print("GPU not detected. Training will use CPU.")

# 4. DEFINE DATASET PATHS
# Training data is used to teach the CNN.
TRAIN_DIR = os.path.join(
    DATASET_DIR,
    "training"
)

# Validation data is used during training to monitor how well the model performs on unseen images.
VALIDATION_DIR = os.path.join(
    DATASET_DIR,
    "validation"
)

# Testing data is kept completely separate from training. It is used only for the final evaluation.
TEST_DIR = os.path.join(
    DATASET_DIR,
    "testing"
)

# 5. CHECK DATASET FOLDERS
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

print(f"Training folder   : {TRAIN_DIR}")
print(f"Validation folder : {VALIDATION_DIR}")
print(f"Testing folder    : {TEST_DIR}")

print("Dataset folders found successfully.")

# 6. IMAGE PREPROCESSING AND DATA AUGMENTATION

# Training images receive data augmentation.
# Data augmentation creates slightly modified versions of training images. This helps the CNN learn more general visual patterns and reduces overfitting.
# rescale:Converts pixel values from 0-255 into approximately 0-1.
# rotation_range: Randomly rotates images slightly.
# width_shift_range / height_shift_range: Slightly moves images horizontally or vertically.
# zoom_range:Randomly zooms images.
# horizontal_flip: Randomly flips images horizontally.
# IMPORTANT: Augmentation is applied ONLY to training data.

training_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=15,
    width_shift_range=0.10,
    height_shift_range=0.10,
    zoom_range=0.10,
    horizontal_flip=True
)


# Validation and testing images should NOT receive random augmentation.Only pixel normalization is applied.
validation_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0
)

test_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0
)

# 7. LOAD TRAINING DATA
print()
print("=" * 70)
print("LOADING TRAINING DATA")
print("=" * 70)

train_generator = training_datagen.flow_from_directory(
    TRAIN_DIR,
       target_size=(IMG_HEIGHT, IMG_WIDTH),  # Resize every image to 224 x 224.
       batch_size=BATCH_SIZE,  # Process 32 images at a time.
       class_mode="binary",  # Binary classification because we have two classes.
       shuffle=True, # Keep class order consistent.
       seed=SEED # Reproducibility.
)

# 8. LOAD VALIDATION DATA

print()
print("=" * 70)
print("LOADING VALIDATION DATA")
print("=" * 70)

validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False   # Validation data does not need to be shuffled.
)

# 9. LOAD TEST DATA

print()
print("=" * 70)
print("LOADING TEST DATA")
print("=" * 70)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode="binary",
    # IMPORTANT: Keep test images in a fixed order.This is required when calculating the confusion matrix and other sklearn metrics.
    shuffle=False
)

# 10. DISPLAY CLASS LABELS

print()
print("=" * 70)
print("CLASS LABELS")
print("=" * 70)

print(train_generator.class_indices)

# Expected output:{'cancer': 0, 'not_cancer': 1}
# The actual order is determined by the folder names.We display it here so we know exactly which label belongs to each class.

# 11. DISPLAY DATASET COUNTS

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

# 12. BUILD THE BASELINE CNN

print()
print("=" * 70)
print("BUILDING BASELINE CNN")
print("=" * 70)

# A Sequential model allows us to add layers one after another.
# This is a simple CNN architecture. It is intentionally much simpler than MobileNet.
# The purpose is to establish a baseline performance against which the MobileNet model can later be compared.

model = Sequential([
       # Convolutional Block 1
    
    # Conv2D learns basic visual features such as: edges, lines and simple patterns.
    layers.Conv2D(
        32,
        (3, 3),
        activation="relu",
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
    ),

    # Reduces the spatial size of feature maps.
    layers.MaxPooling2D(
        pool_size=(2, 2)
    ),

    # Convolutional Block 2
    # Learns more complex features from the previous layer.
    layers.Conv2D(
        64,
        (3, 3),
        activation="relu"
    ),

    layers.MaxPooling2D(
        pool_size=(2, 2)
    ),

    # Convolutional Block 3
    # Learns higher-level image features.
    layers.Conv2D(
        128,
        (3, 3),
        activation="relu"
    ),

    layers.MaxPooling2D(
        pool_size=(2, 2)
    ),

    # Convert Feature Maps to a One-Dimensional Vector

    layers.Flatten(),

      # Fully Connected Layer

    # Combines the learned features to make the final classification decision.
    layers.Dense(
        128,
        activation="relu"
    ),

    # Dropout randomly disables some neurons during training. This helps reduce overfitting.
    layers.Dropout(0.5),

    # Output Layer
    # One output neuron is enough for binary classification. Sigmoid produces a value between 0 and 1. This value represents the probability of class 1.
    layers.Dense(
        1,
        activation="sigmoid"
    )
])


# 13. DISPLAY MODEL ARCHITECTURE

print()
print("=" * 70)
print("BASELINE CNN ARCHITECTURE")
print("=" * 70)

model.summary()

# 14. COMPILE THE MODEL

# Adam is an adaptive optimization algorithm commonly used for training neural networks.
# Binary crossentropy is suitable because this is atwo-class classification problem.
# Accuracy is included as a basic training metric.
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# 15. DEFINE CALLBACKS

# ModelCheckpoint saves the best model during training.
# monitor="val_loss": The model with the lowest validation loss is saved.
# This prevents us from simply using the model from the final epoch if it has started to overfit.
checkpoint_path = os.path.join(
    RESULTS_DIR,
    "baseline_cnn_best.keras"
)

checkpoint = keras.callbacks.ModelCheckpoint(
    checkpoint_path,
    monitor="val_loss",
    save_best_only=True,
    mode="min",
    verbose=1
)


# EarlyStopping stops training if validation performance does not improve for several epochs.
# restore_best_weights=True restores the best model weights.
early_stopping = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True,
    verbose=1
)

# 16. TRAIN THE BASELINE CNN

print()
print("=" * 70)
print("STARTING BASELINE CNN TRAINING")
print("=" * 70)

history = model.fit(
    train_generator,
      validation_data=validation_generator,   # Validation data is used to monitor performance during training.
      epochs=EPOCHS, # Maximum number of epochs. 

       # Save the best model and stop when appropriate.
    callbacks=[ 
        checkpoint,
        early_stopping
    ]
)

# 17. SAVE THE FINAL MODEL

final_model_path = os.path.join(
    RESULTS_DIR,
    "baseline_cnn_final.keras"
)

model.save(final_model_path)

print()
print(f"Final model saved to:")
print(final_model_path)

print()
print(f"Best model saved to:")
print(checkpoint_path)

# 18. PLOT TRAINING AND VALIDATION ACCURACY

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
    "Baseline CNN - Training and Validation Accuracy"
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

# 19. PLOT TRAINING AND VALIDATION LOSS

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
    "Baseline CNN - Training and Validation Loss"
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

# 20. EVALUATE THE MODEL ON TEST DATA

print()
print("=" * 70)
print("EVALUATING BASELINE CNN ON TEST DATA")
print("=" * 70)

# Evaluate the model using the completely unseen test set.
test_loss, test_accuracy = model.evaluate(
    test_generator,
    verbose=1
)

print()
print(f"Test Loss     : {test_loss:.4f}")
print(f"Test Accuracy : {test_accuracy:.4f}")

# 21. GENERATE PREDICTIONS

test_generator.reset() # Reset the generator before prediction to make sure predictions start from the first test image.

# Predict probabilities for all test images.
predicted_probabilities = model.predict(
    test_generator,
    verbose=1
)

# Convert probabilities into binary class predictions.
# Probability >= 0.5 -> class 1
# Probability <  0.5 -> class 0
predicted_classes = (
    predicted_probabilities >= 0.5
).astype(int).flatten()

# 22. GET TRUE TEST LABELS

true_classes = test_generator.classes

# 23. CALCULATE PERFORMANCE METRICS

# Accuracy: Percentage of correctly classified test images.
accuracy = accuracy_score(
    true_classes,
    predicted_classes
)

# Precision: Among images predicted as positive, how many were actually positive.
precision = precision_score(
    true_classes,
    predicted_classes,
    zero_division=0
)

# Recall:
# Among actual positive images,how many were correctly identified.
recall = recall_score(
    true_classes,
    predicted_classes,
    zero_division=0
)

# F1-score: Harmonic mean of precision and recall.
f1 = f1_score(
    true_classes,
    predicted_classes,
    zero_division=0
)

# 24. DISPLAY FINAL METRICS

print()
print("=" * 70)
print("BASELINE CNN FINAL TEST RESULTS")
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

# 25. CLASSIFICATION REPORT

print()
print("=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

# Get the class names in the correct order.
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

# 26. CONFUSION MATRIX

# Confusion matrix shows:True Positive, True Negative, False Positive, False Negative
# It helps us understand exactly where the model is making classification errors.

cm = confusion_matrix(
    true_classes,
    predicted_classes
)

print()
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print(cm)

# 27. SAVE CONFUSION MATRIX AS AN IMAGE

plt.figure(figsize=(7, 6))
plt.imshow(cm, interpolation="nearest" )
plt.title( "Baseline CNN - Confusion Matrix" )
plt.colorbar()
tick_marks = np.arange( len(class_names))
plt.xticks( tick_marks, class_names, rotation=45 )
plt.yticks( tick_marks, class_names )
plt.xlabel( "Predicted Label" )
plt.ylabel( "True Label" )

# Display the actual number inside each cell.
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

# 28. SAVE RESULTS TO A TEXT FILE

results_file = os.path.join(
    RESULTS_DIR,
    "baseline_results.txt"
)

with open(
    results_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(  "BASELINE CNN TEST RESULTS\n" )
    file.write(   "==========================\n\n"  )
    file.write( f"Test Loss: {test_loss:.4f}\n")
    file.write(  f"Accuracy: {accuracy:.4f}\n" )
    file.write( f"Precision: {precision:.4f}\n" )
    file.write( f"Recall: {recall:.4f}\n" )
    file.write(  f"F1-score: {f1:.4f}\n\n"  )
    file.write( "Confusion Matrix:\n"  )
    file.write( str(cm)  )

# 29. FINAL OUTPUT LOCATIONS

print()
print("=" * 70)
print("TRAINING COMPLETED")
print("=" * 70)

print()
print("Results saved in:")

print(RESULTS_DIR)

print()
print("Generated files:")

print("1. baseline_cnn_best.keras")
print("2. baseline_cnn_final.keras")
print("3. accuracy_graph.png")
print("4. loss_graph.png")
print("5. confusion_matrix.png")
print("6. baseline_results.txt")

print()
print("=" * 70)
print("BASELINE CNN PROCESS COMPLETED SUCCESSFULLY")
print("=" * 70)