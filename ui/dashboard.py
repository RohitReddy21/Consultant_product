import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.data_generator import generate_synthetic_data
from services.preprocessing import preprocess_pipeline
from services.segmentation import perform_segmentation
from models.revenue_model import RevenueModel
from models.churn_model import ChurnModel
from services.simulator import PricingSimulator
from reports.report_generator import generate_pdf_report

st.set_page_config(page_title="AI Pricing Strategy Advisor", layout="wide", page_icon="💰")

# --- PREMIUM MODERN CSS ---
st.markdown("""
<style>
    /* Global Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19; /* Deep Slate Background */
        color: #e2e8f0;
    }
    
    /* Headings */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
        letter-spacing: -1px;
    }
    h2, h3 {
        color: #f8fafc;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #60a5fa;
    }
    div[data-testid="metric-container"] label {
        color: #94a3b8;
    }
    
    /* Custom Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
        transition: all 0.2s ease-in-out;
        width: 100%;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8, #4338ca);
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.23);
    }
    
    /* Input Fields */
    .stSelectbox>div>div, .stTextInput>div>div {
        background-color: #1e293b;
        color: white;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    /* ELI5 Box */
    .eli5-box {
        background: rgba(16, 185, 129, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-left: 4px solid #10b981;
        padding: 24px;
        border-radius: 12px;
        color: #d1fae5;
        margin-top: 24px;
        margin-bottom: 24px;
    }
    .eli5-title {
        font-weight: 700;
        font-size: 1.1rem;
        display: block;
        margin-bottom: 12px;
        color: #34d399;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Info Box */
    .stAlert {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'revenue_model' not in st.session_state:
    st.session_state.revenue_model = RevenueModel()
if 'churn_model' not in st.session_state:
    st.session_state.churn_model = ChurnModel()
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = False

# --- Helper: ELI5 Generator ---
def generate_eli5_summary(segment, price_change, result):
    direction = "increase" if price_change > 0 else "decrease"
    change_val = abs(price_change)
    money_emoji = "💸" if result['revenue_uplift_pct'] > 0 else "📉"
    
    summary = f"""
    <div class="eli5-box">
        <span class="eli5-title">🧩 Strategic Insight</span>
        For the <b>{segment}</b> segment, a <b>{change_val}% {direction}</b> in price moves the needle.
        <br><br>
        Key Outcomes:
        <ul>
            <li><b>Revenue:</b> Expected to shift by <b style="color: {'#34d399' if result['revenue_uplift_pct'] > 0 else '#f87171'}">{result['revenue_uplift_pct']:.1f}%</b> {money_emoji}</li>
            <li><b>Retention:</b> Churn risk is estimated at <b>{result['churn_probability']:.1%}</b>.</li>
            <li><b>Verdict:</b> This is categorized as a <b>{result['risk_label']}</b> move.</li>
        </ul>
    </div>
    """
    return summary

# --- Navigation ---
st.sidebar.title("💎 Pricing AI")
st.sidebar.markdown("<div style='font-size: 12px; color: #64748b; margin-top: -15px; margin-bottom: 20px;'>ENTERPRISE EDITION v2.1</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["Data Studio", "Simulation Lab", "Strategy Export"])

# --- PAGE 1: DATA STUDIO ---
if page == "Data Studio":
    st.markdown("<h1>📊 Client Data Studio</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📂 Upload Data")
        uploaded_file = st.file_uploader("Drop Client CSV Here", type="csv")
        if uploaded_file:
            path = f"data/raw/{uploaded_file.name}"
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ Uploaded")
            
            if st.button("🚀 Process & Train AI"):
                with st.spinner("🧠 Analyzing psychology of pricing..."):
                    df = preprocess_pipeline(path)
                    df, _, _ = perform_segmentation(df)
                    st.session_state.df = df
                    st.session_state.revenue_model.train(df)
                    st.session_state.churn_model.train(df)
                    st.session_state.models_trained = True
                st.balloons()
                st.success("AI Models Ready!")

    with c2:
        st.markdown("### 🧪 Demo Mode")
        st.info("Don't have data? Generate a synthetic SaaS dataset.")
        if st.button("🎲 Generate & Load Dummy Data"):
            with st.spinner("Creating virtual customers..."):
                df = generate_synthetic_data(2000)
                path = "data/raw/synthetic_demo.csv"
                df.to_csv(path, index=False)
                df = preprocess_pipeline(path)
                df, _, _ = perform_segmentation(df)
                st.session_state.df = df
                st.session_state.revenue_model.train(df)
                st.session_state.churn_model.train(df)
                st.session_state.models_trained = True
            st.success("Demo Data Active!")

    if st.session_state.df is not None:
        st.markdown("---")
        st.subheader("🔍 Market Segmentation Analysis")
        
        # Fancy Charts
        row1_1, row1_2 = st.columns(2)
        
        with row1_1:
             # Revenue per Segment
            rev_per_seg = st.session_state.df.groupby('segment')['revenue'].sum().reset_index()
            fig_pie = px.pie(rev_per_seg, values='revenue', names='segment', title='Revenue Share by Segment', hole=0.6, color_discrete_sequence=px.colors.sequential.Plasma)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with row1_2:
            # Price vs Limit
            fig_scat = px.scatter(st.session_state.df, x='price', y='units_sold', color='segment', size='revenue', title="Price Elasticity Map", hover_data=['customer_id'], color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_scat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_scat, use_container_width=True)

# --- PAGE 2: SIMULATION LAB ---
elif page == "Simulation Lab":
    st.markdown("<h1>🎛️ Pricing Simulation Lab</h1>", unsafe_allow_html=True)
    
    if not st.session_state.models_trained:
        st.error("⚠️ Please train the AI models in 'Data Studio' first.")
    else:
        df = st.session_state.df
        simulator = PricingSimulator(st.session_state.revenue_model, st.session_state.churn_model)
        
        # Top Controls
        col_ctrl, col_vis = st.columns([1, 2])
        
        with col_ctrl:
            st.markdown("### 🎚️ Settings")
            selected_segment = st.selectbox("Select Segment", df['segment'].unique())
            
            # Baseline Stats
            seg_data = df[df['segment'] == selected_segment]
            curr_price = seg_data['price'].mean()
            curr_units = seg_data['units_sold'].mean()
            curr_disc = seg_data['discount_percent'].mean()
            
            st.markdown(f"""
            <div style='background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <div style='color: #94a3b8; font-size: 12px; text-transform: uppercase;'>Current Price</div>
                <div style='font-size: 24px; font-weight: bold; color: white;'>${curr_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            price_change = st.slider("Price Adjustment (%)", -50, 100, 0, help="Slide to change price")
            
            st.markdown("---")
            st.markdown("### ✨ AI Auto-Pilot")
            if st.button("⚡ Find Optimal Price"):
                summary_data = {'segment': selected_segment, 'avg_price': curr_price, 'avg_units': curr_units, 'avg_discount': curr_disc}
                best_scenario = simulator.find_optimal_price(summary_data)
                
                st.session_state.last_simulation = best_scenario
                st.session_state.auto_optimized = True # Flag to show specific text
                price_change = best_scenario['optimal_price_change'] # Update slider visually (limited in Streamlit, but we simulate the effect)
                st.rerun() # Rerun to update the view with the optimal result
                
        with col_vis:
            st.markdown("### 🎯 Impact Forecast")
            
            summary_data = {'segment': selected_segment, 'avg_price': curr_price, 'avg_units': curr_units, 'avg_discount': curr_disc}
            
            # Check if optimized just ran
            if 'auto_optimized' in st.session_state and st.session_state.auto_optimized:
                result = st.session_state.last_simulation
                price_change = result.get('optimal_price_change', 0)
                st.session_state.auto_optimized = False # Reset
                st.info(f"✨ AI Found the Sweet Spot: {price_change}% Increase!")
            else:
                result = simulator.simulate_scenario(summary_data, price_change)
                st.session_state.last_simulation = result
            
            # Display Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("New Price", f"${result['new_price']:.2f}", f"{price_change}%")
            m2.metric("Rev Uplift", f"{result['revenue_uplift_pct']:.1f}%", delta_color="normal")
            m3.metric("Churn Risk", f"{result['churn_probability']:.1%}", f"{result['churn_increase']:.1%}", delta_color="inverse")
            m4.metric("Risk Score", f"{result['risk_score']}", result['risk_label'])
            
            # ELI5 Section
            st.markdown(generate_eli5_summary(selected_segment, price_change, result), unsafe_allow_html=True)
            
            # Charts showing Baseline vs New
            chart_data = pd.DataFrame({
                "Scenario": ["Current", "Simulated"],
                "Revenue": [100, 100 + result['revenue_uplift_pct']],
                "Churn Probability": [seg_data['churned'].mean()*100, result['churn_probability']*100]
            })
            
            fig = go.Figure(data=[
                go.Bar(name='Revenue Index', x=chart_data['Scenario'], y=chart_data['Revenue'], marker_color='#3b82f6'),
                go.Bar(name='Churn Risk %', x=chart_data['Scenario'], y=chart_data['Churn Probability'], marker_color='#ef4444')
            ])
            fig.update_layout(
                barmode='group', 
                title="Before vs After Comparison", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font={'color': "white"},
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        # --- SENSITIVITY ANALYSIS ---
        st.markdown("---")
        st.markdown("### 📈 Sensitivity Analysis")
        st.caption("How does Revenue and Churn react to different price points?")
        
        # Calculate curve
        x_vals = []
        y_rev = []
        y_churn = []
        
        for p in range(-50, 101, 5):
            sim = simulator.simulate_scenario(summary_data, p)
            x_vals.append(p)
            y_rev.append(sim['revenue_uplift_pct'])
            y_churn.append(sim['churn_probability'] * 100)
            
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(x=x_vals, y=y_rev, mode='lines+markers', name='Revenue Uplift %', line=dict(color='#34d399', width=3)))
        fig_sens.add_trace(go.Scatter(x=x_vals, y=y_churn, mode='lines+markers', name='Churn Risk %', line=dict(color='#f87171', width=3, dash='dot')))
        
        # Add a vertical line for current selection
        fig_sens.add_vline(x=price_change, line_width=2, line_dash="dash", line_color="white", annotation_text="Selected")
        
        fig_sens.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font={'color': "white"},
            xaxis_title="Price Change (%)",
            yaxis_title="Impact (%)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_sens, use_container_width=True)


# --- PAGE 3: STRATEGY REPORT ---
elif page == "Strategy Export":
    st.markdown("<h1>📑 Executive Report Generation</h1>", unsafe_allow_html=True)
    
    if 'last_simulation' not in st.session_state:
        st.info("⚠️ Run a simulation first.")
    else:
        res = st.session_state.last_simulation
        st.write("### Preview of Recommendation")
        
        st.markdown(f"""
        <div style='background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155;'>
            <h3 style='color: #3b82f6;'>Executive Summary</h3>
            <p>For the <b>{res['segment']}</b> segment, we recommend a price adjustment of <b>{((res['new_price'] - res['old_price'])/res['old_price'])*100:.0f}%</b>.</p>
            <p>This aligns with a <b>{res['risk_label']}</b> strategy, projecting a <b>{res['revenue_uplift_pct']:.1f}%</b> increase in revenue with a manageable churn of <b>{res['churn_probability']:.1%}</b>.</p>
            <br>
            <p style='font-size: 0.9em; color: #94a3b8;'>Generated by AI Pricing Strategy Advisor</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("📄 Generate PDF Report"):
            path = "reports/final_strategy_report.pdf"
            generate_pdf_report([res], path)
            with open(path, "rb") as f:
                st.download_button("Download Official Consultant Report", f, file_name="Pricing_Strategy_Report.pdf")
