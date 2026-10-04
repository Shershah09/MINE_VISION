from pathlib import Path

import joblib
import pandas as pd
from ultralytics import YOLO


# ============================================================
# PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# DEVICE
# Render Free Instance has no GPU
# Therefore, use CPU for all YOLO inference
# ============================================================

DEVICE = "cpu"


# ============================================================
# LOAD AI MODELS
# ============================================================

# ---------- Gas Risk Model ----------
gas_model = joblib.load(
    BASE_DIR / "models" / "gas_risk_model_v1.joblib"
)


# ---------- Helmet Detection Model ----------
helmet_model = YOLO(
    BASE_DIR / "models" / "vision" / "helmet" / "best.pt"
)


# ---------- Worker Detection Model ----------
worker_model = YOLO(
    BASE_DIR / "yolo11n.pt"
)


# ---------- Fire / Smoke Detection Model ----------
fire_smoke_model = YOLO(
    BASE_DIR / "models" / "vision" / "fire_smoke" / "best.pt"
)


# ============================================================
# RUN AI
# ============================================================

def run_ai(image_path, sensor_data):

    # ========================================================
    # 1. GAS AI
    # ========================================================

    gas_df = pd.DataFrame([sensor_data])

    gas_risk = gas_model.predict(gas_df)[0]


    # ========================================================
    # 2. HELMET DETECTION
    # ========================================================

    helmet_result = helmet_model(
        image_path,
        device=DEVICE,
        conf=0.25,
        verbose=False
    )[0]


    # ========================================================
    # 3. WORKER DETECTION
    # ========================================================

    worker_result = worker_model(
        image_path,
        device=DEVICE,
        classes=[0],
        conf=0.35,
        verbose=False
    )[0]


    # ========================================================
    # 4. FIRE / SMOKE DETECTION
    # ========================================================

    fire_smoke_result = fire_smoke_model(
        image_path,
        device=DEVICE,
        conf=0.55,
        verbose=False
    )[0]


    # ========================================================
    # 5. PROCESS HELMET DETECTION
    # ========================================================

    helmet_detected = False
    no_helmet_detected = False

    for box in helmet_result.boxes:

        class_id = int(box.cls[0])

        name = helmet_model.names[class_id]

        if name == "Hardhat":
            helmet_detected = True

        elif name == "NO-Hardhat":
            no_helmet_detected = True


    # ========================================================
    # 6. PROCESS WORKER DETECTION
    # ========================================================

    worker_detected = len(worker_result.boxes) > 0


    # ========================================================
    # 7. PROCESS FIRE / SMOKE DETECTION
    # ========================================================

    fire_detected = False
    smoke_detected = False

    for box in fire_smoke_result.boxes:

        class_id = int(box.cls[0])

        name = fire_smoke_model.names[class_id]

        if name == "fire":
            fire_detected = True

        elif name == "smoke":
            smoke_detected = True


    # ========================================================
    # 8. VISION RISK
    # ========================================================

    if fire_detected:

        vision_risk = "CRITICAL"

    elif smoke_detected:

        vision_risk = "WARNING"

    elif no_helmet_detected:

        vision_risk = "WARNING"

    else:

        vision_risk = "SAFE"


    # ========================================================
    # 9. OVERALL RISK
    # ========================================================

    risk_order = {
        "SAFE": 0,
        "WARNING": 1,
        "DANGER": 2,
        "CRITICAL": 3
    }


    overall_risk = (
        gas_risk
        if risk_order[gas_risk] >= risk_order[vision_risk]
        else vision_risk
    )


    # ========================================================
    # 10. RETURN RESULTS
    # ========================================================

    return {

        "gas_risk": gas_risk,

        "worker": (
            "DETECTED"
            if worker_detected
            else "NOT DETECTED"
        ),

        "helmet": (
            "HARDHAT"
            if helmet_detected
            else "NO-HARDHAT"
            if no_helmet_detected
            else "NOT DETECTED"
        ),

        "fire": (
            "DETECTED"
            if fire_detected
            else "NOT DETECTED"
        ),

        "smoke": (
            "DETECTED"
            if smoke_detected
            else "NOT DETECTED"
        ),

        "vision_risk": vision_risk,

        "overall_risk": overall_risk
    }
