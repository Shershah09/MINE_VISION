from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
import shutil
import traceback

app = FastAPI(title="MineSafetyAI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://shershah09.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return {
        "project": "MineSafetyAI",
        "status": "Backend running"
    }


@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),

    CH4: float = Form(...),
    CO: float = Form(...),
    CO2: float = Form(...),
    O2: float = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...)
):

    try:

        print("========== ANALYZE START ==========")

        print("Image received:", image.filename)

        image_path = UPLOAD_DIR / image.filename

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        print("Image saved:", image_path)

        sensor_data = {
            "CH4": CH4,
            "CO": CO,
            "CO2": CO2,
            "O2": O2,
            "temperature": temperature,
            "humidity": humidity
        }

        print("Sensor data:", sensor_data)

        # TEMPORARY TEST
        # We are NOT running AI yet.

        return {
            "status": "SUCCESS",
            "message": "Image upload and sensor data received successfully",
            "image": image.filename,
            "sensor_data": sensor_data
        }

    except Exception as e:

        print("========== ANALYZE ERROR ==========")
        print(str(e))
        traceback.print_exc()

        return {
            "status": "ERROR",
            "error": str(e)
        }
