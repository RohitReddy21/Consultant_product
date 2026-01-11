from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
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
from reports.report_generator import generate_pdf_report
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
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# Global Dataframe storage (simplification for demo)
global_df = None

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
    global global_df
    print("🚀 API Startup: Generating synthetic data and training models...")
    try:
        # Generate data
        global_df = generate_synthetic_data(2000)
        # Train
        revenue_model.train(global_df)
        churn_model.train(global_df)
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
async def upload_data(file: UploadFile = File(...)):
    global global_df
    file_location = f"{DATA_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Trigger processing pipeline
    try:
        df = preprocess_pipeline(file_location)
        df, _, _ = perform_segmentation(df)
        global_df = df # Update global state
        
        # Retrain immediately
        revenue_model.train(df)
        churn_model.train(df)
        
        return {"message": "File uploaded and processed successfully", "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train_models")
async def train_models():
    global global_df
    # Generate fresh synthetic
    global_df = generate_synthetic_data(2000)
    
    revenue_model.train(global_df)
    churn_model.train(global_df)
    
    return {"message": "Models trained successfully"}

@app.get("/analytics")
async def get_analytics():
    global global_df
    if global_df is None:
         # Fallback
         global_df = generate_synthetic_data(1000)
    
    # Simple aggregation for charts
    rev_by_seg = global_df.groupby('segment')['revenue'].sum().to_dict()
    churn_rate = global_df['churned'].mean()
    
    # Scatter Data (Sample 100 points for performance)
    scatter_df = global_df.sample(min(100, len(global_df)))
    scatter_data = scatter_df[['price', 'units_sold', 'segment']].to_dict(orient='records')
    
    return {
        "revenue_by_segment": rev_by_seg,
        "total_revenue": global_df['revenue'].sum(),
        "churn_rate": churn_rate,
        "scatter_data": scatter_data
    }

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    if revenue_model.model is None:
         # Emergency auto-train
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

class ReportRequest(BaseModel):
    results: dict

@app.post("/generate_report")
async def generate_report(request: ReportRequest):
    try:
        filename = "strategy_report.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        # The generator expects a list of scenarios
        generate_pdf_report([request.results], filepath)
        
        return FileResponse(filepath, media_type='application/pdf', filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
