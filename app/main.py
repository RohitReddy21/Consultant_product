from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import pandas as pd
from services.preprocessing import preprocess_pipeline
from services.segmentation import perform_segmentation
from models.revenue_model import RevenueModel
from models.churn_model import ChurnModel
from services.simulator import PricingSimulator
from services.data_generator import generate_synthetic_data
from app.auth import create_access_token, get_current_user, verify_password, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, status

app = FastAPI(title="AI Pricing Strategy Advisor API")

# Allow CORS for React Frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (in a real app, use a proper model registry or dependency injection)
revenue_model = RevenueModel()
churn_model = ChurnModel()
simulator = PricingSimulator(revenue_model, churn_model)

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

class SimulationRequest(BaseModel):
    segment: str
    current_price: float
    current_discount: float
    current_units: float
    price_change_pct: float

# Dummy User DB
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("secret")
    }
}

@app.on_event("startup")
async def startup_event():
    print("🚀 API Startup: Generating synthetic data and training models...")
    try:
        # Generate data
        df = generate_synthetic_data(2000)
        # Train
        revenue_model.train(df)
        churn_model.train(df)
        print("✅ Models trained and ready on startup!")
    except Exception as e:
        print(f"❌ Startup training failed: {e}")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload_data")
async def upload_data(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    file_location = f"{DATA_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Trigger processing pipeline
    try:
        df = preprocess_pipeline(file_location)
        # Save processed?
        return {"message": "File uploaded and processed successfully", "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train_models")
async def train_models():
    # Load latest data (simplification)
    # real app would track dataset IDs
    files = os.listdir(DATA_DIR)
    if not files:
         # Fallback to synthetic if no files
        df = generate_synthetic_data(2000)
    else:
        filepath = os.path.join(DATA_DIR, files[0]) # take first
        df = preprocess_pipeline(filepath)
        df, _, _ = perform_segmentation(df)
    
    revenue_model.train(df)
    churn_model.train(df)
    
    return {"message": "Models trained successfully"}

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    if revenue_model.model is None:
         # Emergency auto-train if not ready (should be covered by startup, but safe fallback)
        df = generate_synthetic_data(1000)
        revenue_model.train(df)
        churn_model.train(df)
        
    summary = {
        'segment': request.segment,
        'avg_price': request.current_price,
        'avg_discount': request.current_discount,
        'avg_units': request.current_units
    }
    
    result = simulator.simulate_scenario(summary, request.price_change_pct)
    return result

@app.get("/")
def read_root():
    return {"message": "AI Pricing Strategy Advisor API is running"}
