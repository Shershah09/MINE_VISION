import joblib
import pandas as pd


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_PATH = "models/gas_risk_model_v1.joblib"

model = joblib.load(MODEL_PATH)


# ============================================================
# SENSOR INPUT
# ============================================================

sensor_data = {
    "CH4": 0.85,
    "CO": 45,
    "CO2": 0.32,
    "O2": 19.1,
    "temperature": 34,
    "humidity": 82
}


# ============================================================
# CREATE INPUT DATAFRAME
# ============================================================

input_data = pd.DataFrame([sensor_data])


# ============================================================
# PREDICT
# ============================================================

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(
    input_data
)[0]

classes = model.classes_


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n========================================")
print("MINE SAFETY AI - GAS RISK PREDICTION")
print("========================================")

print("\nSensor readings:")

for sensor, value in sensor_data.items():
    print(f"{sensor:12}: {value}")


print("\nPredicted Risk:")
print(prediction)


print("\nRisk Probabilities:")

for class_name, probability in zip(
    classes,
    probabilities
):
    print(
        f"{class_name:10}: "
        f"{probability * 100:.2f}%"
    )