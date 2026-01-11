import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Float, MeshDistortMaterial, Stars, Sparkles } from '@react-three/drei';
import axios from 'axios';
import './App.css';

// --- 3D Background Component ---
function PricingCrystal({ riskLevel }) {
  const meshRef = useRef();

  const getColor = () => {
    if (riskLevel === 'High') return '#ef4444';
    if (riskLevel === 'Medium') return '#f59e0b';
    return '#10b981';
  };

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    meshRef.current.rotation.x = time * 0.15;
    meshRef.current.rotation.y = time * 0.2;
    const scale = 1 + Math.sin(time * 1.5) * 0.03;
    meshRef.current.scale.set(scale, scale, scale);
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2.5, 0]} />
        <MeshDistortMaterial
          color={getColor()}
          distort={0.3}
          speed={1.5}
          roughness={0.1}
          metalness={0.8}
          emissive={getColor()}
          emissiveIntensity={0.2}
          wireframe={false}
        />
      </mesh>
    </Float>
  );
}

function Global3DBackground({ riskLevel }) {
  return (
    <div className="canvas-container">
      <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
        <color attach="background" args={['#0b0f19']} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#3b82f6" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ec4899" />
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={0.5} />
        <Sparkles count={40} scale={12} size={3} speed={0.3} opacity={0.4} color="#60a5fa" />
        <PricingCrystal riskLevel={riskLevel} />
        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.3} />
      </Canvas>
    </div>
  );
}

// --- UI Components ---

function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { id: 'data', label: '📊 Data Studio' },
    { id: 'sim', label: '🧪 Simulation Lab' },
    { id: 'export', label: '📑 Strategy Export' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">💎</div>
        <div className="logo-text">
          <h1>Pricing AI</h1>
          <span>ENTERPRISE v2.1</span>
        </div>
      </div>

      <nav>
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot"></div> Connected to Brain
      </div>
    </div>
  );
}

function MetricCard({ label, value, subValue, type = 'neutral' }) {
  let colorClass = 'neutral';
  if (type === 'good') colorClass = 'text-green';
  if (type === 'bad') colorClass = 'text-red';

  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${colorClass}`}>{value}</div>
      {subValue && <div className="metric-sub">{subValue}</div>}
    </div>
  );
}

// --- Pages ---

function DataStudio({ onTrain, loading }) {
  return (
    <div className="page-content fade-in">
      <h1 className="page-title">Client Data Studio</h1>

      <div className="grid-2-col">
        <div className="card upload-section">
          <h2>📂 Upload Data</h2>
          <div className="upload-box">
            <span className="icon">☁️</span>
            <p>Drag and drop client CSV here</p>
            <button className="secondary-btn" onClick={() => alert("Upload feature coming in v2.2")}>Browse Files</button>
          </div>
        </div>

        <div className="card demo-section">
          <h2>🧪 Demo Mode</h2>
          <div className="info-box">
            Don't have data? Generate a synthetic SaaS dataset to test the AI models immediately.
          </div>
          <button
            className="primary-btn full-width"
            onClick={onTrain}
            disabled={loading}
          >
            {loading ? '🧠 Training AI Models...' : '🎲 Generate & Load Dummy Data'}
          </button>
        </div>
      </div>

      <div className="card chart-placeholder">
        <h2>🔍 Market Segmentation Analysis</h2>
        <div className="placeholder-graph">
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            [Analysis Charts require real data]
          </div>
        </div>
      </div>
    </div>
  );
}

function SimulationLab({ priceChange, setPriceChange, onSimulate, results, loading }) {
  return (
    <div className="page-content fade-in">
      <div className="header-row">
        <h1 className="page-title">Pricing Simulation Lab</h1>
        {results && <div className="badge">Risk: {results.risk_label}</div>}
      </div>

      <div className="sim-layout">
        {/* Left Column: Controls */}
        <div className="sim-controls">
          <div className="card">
            <h2>🎚️ Settings</h2>

            <div className="input-group">
              <label>Segment</label>
              <select className="styled-select">
                <option>SMB</option>
                <option>Enterprise</option>
                <option>Mid-Market</option>
              </select>
            </div>

            <div className="current-price-box">
              <div className="label">CURRENT PRICE</div>
              <div className="price">$100.00</div>
            </div>

            <div className="slider-group">
              <div className="slider-header">
                <label>Price Adjustment</label>
                <span className="slider-val">{priceChange > 0 ? '+' : ''}{priceChange}%</span>
              </div>
              <input
                type="range"
                min="-50" max="50"
                value={priceChange}
                onChange={(e) => setPriceChange(Number(e.target.value))}
              />
            </div>

            <div className="divider"></div>

            <h3>✨ AI Auto-Pilot</h3>
            <button
              className="primary-btn full-width"
              onClick={onSimulate}
              disabled={loading}
            >
              {loading ? '🧠 Crunching Numbers...' : '⚡ Find Optimal Price'}
            </button>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="sim-results">
          {results ? (
            <>
              <div className="metrics-grid">
                <MetricCard
                  label="New Price"
                  value={`$${results.new_price.toFixed(2)}`}
                  subValue={`${priceChange}%`}
                />
                <MetricCard
                  label="Revenue Uplift"
                  value={`${results.revenue_uplift_pct >= 0 ? '+' : ''}${results.revenue_uplift_pct.toFixed(1)}%`}
                  type={results.revenue_uplift_pct >= 0 ? 'good' : 'bad'}
                />
                <MetricCard
                  label="Churn Probability"
                  value={results.churn_probability}
                  type="bad"
                  subValue="Risk Level"
                />
              </div>

              <div className="card eli5-box">
                <div className="eli5-title">🧩 Strategic Insight</div>
                <p>
                  For the <b>SMB</b> segment, a <b>{Math.abs(priceChange)}% {priceChange > 0 ? 'increase' : 'decrease'}</b> in price moves the needle.
                </p>
                <br />
                <ul>
                  <li>Expected revenue shift: <b>{results.revenue_uplift_pct.toFixed(1)}%</b></li>
                  <li>This is categorized as a <b>{results.risk_label}</b> move.</li>
                </ul>
              </div>
            </>
          ) : (
            <div className="card empty-state">
              <div className="empty-icon">👈</div>
              <h3>Ready to Simulate</h3>
              <p>Adjust the slider and click "Find Optimal Price" to see the AI predictions.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --- Main App Root ---

export default function App() {
  const [activePage, setActivePage] = useState('sim');
  const [priceChange, setPriceChange] = useState(0);
  const [results, setResults] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [trainLoading, setTrainLoading] = useState(false);
  const [riskLevel, setRiskLevel] = useState('Low');

  const handleSimulate = async () => {
    setSimLoading(true);
    try {
      const payload = {
        segment: "SMB",
        current_price: 100.0,
        current_discount: 0.1,
        current_units: 1000,
        price_change_pct: priceChange
      };
      // Connect to Python Backend
      const response = await axios.post('http://localhost:8000/simulate', payload);
      const data = response.data;

      setResults({
        revenue_uplift_pct: data.revenue_uplift_pct,
        churn_probability: (data.churn_probability * 100).toFixed(1) + '%',
        risk_label: data.risk_label,
        new_price: data.new_price
      });
      setRiskLevel(data.risk_label);
    } catch (error) {
      console.error(error);
      alert("Backend offline? Ensure uvicorn is running on port 8000");
    }
    setSimLoading(false);
  };

  const handleTrain = async () => {
    setTrainLoading(true);
    try {
      await axios.post('http://localhost:8000/train_models');
      alert("✅ Success! New synthetic data generated and AI models retrained.");
    } catch (error) {
      console.error(error);
      alert("Error training models. Check backend console.");
    }
    setTrainLoading(false);
  };

  return (
    <div className="app-shell">
      {/* 3D Layer acts as wallpaper */}
      <Global3DBackground riskLevel={riskLevel} />

      {/* Sidebar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <main className="main-content">
        {activePage === 'data' && (
          <DataStudio
            onTrain={handleTrain}
            loading={trainLoading}
          />
        )}
        {activePage === 'sim' && (
          <SimulationLab
            priceChange={priceChange}
            setPriceChange={setPriceChange}
            onSimulate={handleSimulate}
            results={results}
            loading={simLoading}
          />
        )}
        {activePage === 'export' && (
          <div className="page-content fade-in">
            <h1 className="page-title">Executive Report</h1>
            <div className="card">
              <p>Simulation results must be generated first.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
