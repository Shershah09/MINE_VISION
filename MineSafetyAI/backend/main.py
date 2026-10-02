from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
from backend.ai_service import run_ai
from pathlib import Path
import shutil


app = FastAPI(title="MineSafetyAI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload folder
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

    # Save uploaded image
    image_path = UPLOAD_DIR / image.filename

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)


    # Sensor data
    sensor_data = {
        "CH4": CH4,
        "CO": CO,
        "CO2": CO2,
        "O2": O2,
        "temperature": temperature,
        "humidity": humidity
    }


    # Run Gas AI + Vision AI
    result = run_ai(
        str(image_path),
        sensor_data
    )


    return {
        "image": image.filename,
        "ai_result": result
    }