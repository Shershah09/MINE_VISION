import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/synthetic/gas/synthetic_gas_data_v2.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset loaded")
print("Shape:", df.shape)


# ============================================================
# 2. DEFINE FEATURES AND TARGET
# ============================================================

FEATURES = [
    "CH4",
    "CO",
    "CO2",
    "O2",
    "temperature",
    "humidity"
]

TARGET = "risk_level"


X = df[FEATURES]
y = df[TARGET]


# ============================================================
# 3. SPLIT BY LOCATION
# ============================================================

# We intentionally do NOT use train_test_split.
# Consecutive readings from the same location are very similar.
#
# Training locations:
# L01-L14
#
# Validation locations:
# L15-L17
#
# Test locations:
# L18-L20

train_locations = [
    f"L{i:02d}" for i in range(1, 15)
]

validation_locations = [
    "L15",
    "L16",
    "L17"
]

test_locations = [
    "L18",
    "L19",
    "L20"
]


train_df = df[
    df["location_id"].isin(train_locations)
]

validation_df = df[
    df["location_id"].isin(validation_locations)
]

test_df = df[
    df["location_id"].isin(test_locations)
]


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ============================================================
# 4. DISPLAY SPLIT INFORMATION
# ============================================================

print("\nData split")

print(
    "Training:",
    X_train.shape
)

print(
    "Validation:",
    X_validation.shape
)

print(
    "Testing:",
    X_test.shape
)


# ============================================================
# 5. CREATE MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# ============================================================
# 6. TRAIN
# ============================================================

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# 7. VALIDATION
# ============================================================

validation_predictions = model.predict(
    X_validation
)

validation_accuracy = accuracy_score(
    y_validation,
    validation_predictions
)

print("\nValidation Accuracy:")
print(
    f"{validation_accuracy:.4f}"
)

print("\nValidation Report:")

print(
    classification_report(
        y_validation,
        validation_predictions
    )
)


# ============================================================
# 8. FINAL TEST
# ============================================================

test_predictions = model.predict(
    X_test
)

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

print("\n========================================")
print("FINAL TEST RESULTS")
print("========================================")

print(
    f"Test Accuracy: {test_accuracy:.4f}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions
    )
)


# ============================================================
# 9. CONFUSION MATRIX
# ============================================================

labels = [
    "SAFE",
    "WARNING",
    "DANGER",
    "CRITICAL"
]

matrix = confusion_matrix(
    y_test,
    test_predictions,
    labels=labels
)

print("\nConfusion Matrix:")

print(
    pd.DataFrame(
        matrix,
        index=labels,
        columns=labels
    )
)


# ============================================================
# 10. FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({

    "feature": FEATURES,

    "importance": model.feature_importances_

})

importance = importance.sort_values(
    "importance",
    ascending=False
)


print("\nFeature Importance:")

print(
    importance.to_string(
        index=False
    )
)


# ============================================================
# 11. SAVE MODEL
# ============================================================

MODEL_PATH = "models/gas_risk_model_v1.joblib"

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved to:")

print(MODEL_PATH)