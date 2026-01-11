# AI Pricing Strategy Advisor

A consultant-grade SaaS tool for simulating pricing decisions, predicting revenue impact, and assessing churn risk using AI.

## 🚀 Project Structure

```
pricing-ai-consultant/
│
├── data/               # Raw and processed data
├── models/             # ML Models (Revenue & Churn)
├── services/           # Core Logic (Preprocessing, Segmentation, Simulation)
├── reports/            # PDF Report Generation
├── app/                # FastAPI Backend (SaaS API)
├── ui/                 # Streamlit Dashboard (Consultant Interface)
└── requirements.txt    # Dependencies
```

## 🛠️ How to Run Locally

### Prerequisites
- Python 3.8+
- VS Code (Recommended)

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Consultant Dashboard (UI):
   ```bash
   streamlit run ui/dashboard.py
   ```
   *This will open the dashboard in your browser. This is the primary interface for consultants.*

3. (Optional) Run the SaaS Backend (API):
   ```bash
   uvicorn app.main:app --reload
   ```
   *Access API docs at http://127.0.0.1:8000/docs*

## 💼 How Consultants Use It

1. **Client Engagement**: Request historical transaction data from the client (CSV).
2. **Data Ingestion**: Upload the CSV into the "Data Upload" tab.
3. **Training**: Click "Process & Train Models". The AI learns price elasticity and churn sensitivity for each segment.
4. **Simulation**:
   - Go to "Pricing Simulator".
   - Select a customer segment (e.g., SMB, Enterprise).
   - Use sliders to test a price increase (e.g., +10%).
   - Observe the **Revenue Upside** vs. **Churn Risk**.
5. **Strategy Formulation**: Iterate until you find the "Sweet Spot" (high revenue, acceptable risk).
6. **Deliverable**: Go to "Strategy Report" and generate the PDF. Present this executive report to the client.

## 💰 How to Sell It (Business Model)

### 1. High-Ticket Consulting (₹3L - ₹10L per project)
- **Value Prop**: "We use proprietary AI to scientifically determine your optimal pricing, minimizing the risk of a botched price hike."
- **Deliverable**: The PDF Strategy Report + Presentation.
- **Process**: You use the tool as your "secret weapon" to deliver results faster and with more confidence than traditional spreadsheets.

### 2. SaaS Subscription (₹50k - ₹1L / month)
- **Target**: CFOs and Heads of Revenue at large SaaS companies.
- **Value Prop**: "Continuous pricing optimization. Monitor how market shifts affect your pricing power month-over-month."
- **Delivery**: Deploy the `app/main.py` backend and a React/Streamlit frontend on AWS/Azure. Give them login access (JWT Auth is already implemented).

## 🧠 AI Models Explanation

- **Revenue Model**: Random Forest Regressor. Predicts `units_sold` (demand) based on Price, Discount, and Segment. Captures price elasticity (non-linear).
- **Churn Model**: Logistic Regression. Predicts probability of churn based on Price and Segment characteristics.
- **Risk Scoring**: A composite score weighted by High Churn Probability (Downside) vs. Revenue Uplift (Upside).

---
*Built for the Modern Consultant.*
