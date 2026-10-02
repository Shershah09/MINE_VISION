from ultralytics import YOLO


# ==========================================
# 1. LOAD MODELS
# ==========================================

helmet_model = YOLO("models/vision/helmet/best.pt")
worker_model = YOLO("yolo11n.pt")
fire_smoke_model = YOLO("models/vision/fire_smoke/best.pt")


# ==========================================
# 2. IMAGE TO ANALYZE
# ==========================================

IMAGE = "smoke_test.jpg"


# ==========================================
# 3. HELMET DETECTION
# ==========================================

helmet_result = helmet_model(
    IMAGE,
    device=0,
    conf=0.25,
    verbose=False
)[0]

helmet_detected = False
no_helmet_detected = False

for box in helmet_result.boxes:
    class_id = int(box.cls[0])
    class_name = helmet_model.names[class_id]
    confidence = float(box.conf[0])

    if class_name == "Hardhat":
        helmet_detected = True
        print(f"Helmet: Hardhat ({confidence:.2f})")

    elif class_name == "NO-Hardhat":
        no_helmet_detected = True
        print(f"Helmet: NO-Hardhat ({confidence:.2f})")


# ==========================================
# 4. WORKER DETECTION
# ==========================================

worker_result = worker_model(
    IMAGE,
    device=0,
    classes=[0],
    conf=0.35,
    verbose=False
)[0]

worker_detected = len(worker_result.boxes) > 0

if worker_detected:
    print(f"Worker: {len(worker_result.boxes)} detected")
else:
    print("Worker: Not detected")


# ==========================================
# 5. FIRE + SMOKE DETECTION
# ==========================================

fire_smoke_result = fire_smoke_model(
    IMAGE,
    device=0,
    conf=0.25,
    verbose=False
)[0]

fire_detected = False
smoke_detected = False

for box in fire_smoke_result.boxes:
    class_id = int(box.cls[0])
    class_name = fire_smoke_model.names[class_id]
    confidence = float(box.conf[0])

    if class_name == "fire":
        fire_detected = True
        print(f"Fire: Detected ({confidence:.2f})")

    elif class_name == "smoke":
        smoke_detected = True
        print(f"Smoke: Detected ({confidence:.2f})")


# ==========================================
# 6. VISION DECISION
# ==========================================

if fire_detected:
    vision_risk = "CRITICAL"

elif smoke_detected:
    vision_risk = "WARNING"

elif worker_detected and no_helmet_detected:
    vision_risk = "WARNING"

else:
    vision_risk = "SAFE"


# ==========================================
# 7. FINAL RESULT
# ==========================================

print()
print("=" * 40)
print("        MINE SAFETY VISION AI")
print("=" * 40)

print(f"Worker       : {'DETECTED' if worker_detected else 'NOT DETECTED'}")

if helmet_detected:
    print("Helmet       : HARDHAT")
elif no_helmet_detected:
    print("Helmet       : NO-HARDHAT")
else:
    print("Helmet       : NOT DETECTED")

print(f"Fire         : {'DETECTED' if fire_detected else 'NOT DETECTED'}")
print(f"Smoke        : {'DETECTED' if smoke_detected else 'NOT DETECTED'}")

print("-" * 40)
print(f"VISION RISK  : {vision_risk}")
print("=" * 40)