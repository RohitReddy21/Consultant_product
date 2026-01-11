import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Float, MeshDistortMaterial, Stars, Sparkles } from '@react-three/drei';
import axios from 'axios';
import './App.css';

// --- 3D Components ---

function Crystal({ priceChange, riskLevel }) {
  const meshRef = useRef();

  // Color logic based on Risk
  const getColor = () => {
    if (riskLevel === 'High') return '#ef4444'; // Red
    if (riskLevel === 'Medium') return '#f59e0b'; // Orange
    return '#10b981'; // Green
  };

  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    meshRef.current.rotation.x = time * 0.2;
    meshRef.current.rotation.y = time * 0.3;
    // Pulse effect
    const scale = 1 + Math.sin(time * 2) * 0.05;
    meshRef.current.scale.set(scale, scale, scale);
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2, 0]} /> {/* Low poly look */}
        <MeshDistortMaterial
          color={getColor()}
          distort={0.4}
          speed={2}
          roughness={0}
          metalness={0.9}
          emissive={getColor()}
          emissiveIntensity={0.2}
        />
      </mesh>
    </Float>
  );
}

function FloatingText({ text, position, size = 1 }) {
  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.2}>
      <Text
        position={position}
        fontSize={size}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff"
      >
        {text}
      </Text>
    </Float>
  );
}

// --- UI Components ---

function ControlPanel({ priceChange, setPriceChange, onSimulate, isLoading }) {
  return (
    <div className="panel left-panel fade-in">
      <h2>🎛️ Controls</h2>
      <div className="control-group">
        <label>Price Adjustment</label>
        <div className="slider-container">
          <input
            type="range"
            min="-50"
            max="50"
            value={priceChange}
            onChange={(e) => setPriceChange(Number(e.target.value))}
          />
          <span className="value-display">{priceChange > 0 ? '+' : ''}{priceChange}%</span>
        </div>
      </div>

      <button onClick={onSimulate} disabled={isLoading} className="simulate-btn">
        {isLoading ? 'Calculating...' : '🔮 Simulate Scenario'}
      </button>
    </div>
  );
}

function StatsPanel({ results }) {
  if (!results) return null;

  return (
    <div className="panel right-panel fade-in">
      <h2>📊 Projected Impact</h2>

      <div className="stat-card">
        <div className="label">Revenue Uplift</div>
        <div className="value" style={{ color: results.revenue_uplift_pct >= 0 ? '#34d399' : '#f87171' }}>
          {results.revenue_uplift_pct >= 0 ? '▲' : '▼'} {Math.abs(results.revenue_uplift_pct).toFixed(1)}%
        </div>
      </div>

      <div className="stat-card">
        <div className="label">Churn Risk</div>
        <div className="value" style={{ color: '#f87171' }}>
          {results.churn_probability}
        </div>
        <div className="sub-value">Probability</div>
      </div>

      <div className="stat-card">
        <div className="label">Risk Assessment</div>
        <div className="risk-badge" data-level={results.risk_label}>
          {results.risk_label}
        </div>
      </div>
    </div>
  );
}

// --- Main App ---

export default function App() {
  const [priceChange, setPriceChange] = useState(0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [riskLevel, setRiskLevel] = useState('Low');

  // Initial Simulation
  useEffect(() => {
    // Basic mock init, real app would fetch current user state
  }, []);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      // Hardcoded "current state" for demo purposes, matching the Python demo data logic
      const payload = {
        segment: "SMB", // Defaulting to SMB
        current_price: 100.0,
        current_discount: 0.1,
        current_units: 1000,
        price_change_pct: priceChange
      };

      // Ensure your backend is running on port 8000
      const response = await axios.post('http://localhost:8000/simulate', payload);
      const data = response.data;

      // Transform data for UI
      setResults({
        revenue_uplift_pct: data.revenue_uplift_pct,
        churn_probability: (data.churn_probability * 100).toFixed(1) + '%',
        risk_label: data.risk_label,
        new_price: data.new_price
      });
      setRiskLevel(data.risk_label); // Update 3D color

    } catch (error) {
      console.error("Simulation error:", error);
      alert("Failed to connect to AI Backend. Make sure 'uvicorn app.main:app' is running!");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* 3D Background */}
      <div className="canvas-layer">
        <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
          <color attach="background" args={['#050505']} />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#4da6ff" />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ff00ff" />

          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          <Sparkles count={50} scale={10} size={4} speed={0.4} opacity={0.5} color="#4da6ff" />

          <Crystal priceChange={priceChange} riskLevel={riskLevel} />

          <FloatingText text={`${priceChange > 0 ? '+' : ''}${priceChange}%`} position={[0, 2.5, 0]} size={0.5} />
          {results && (
            <FloatingText text={`$${results.new_price.toFixed(2)}`} position={[0, -2.5, 0]} size={0.3} />
          )}

          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </div>

      {/* UI Overlay */}
      <div className="ui-layer">
        <header className="app-header">
          <h1>🔮 AI Pricing Consultant</h1>
        </header>

        <main className="main-layout">
          <ControlPanel
            priceChange={priceChange}
            setPriceChange={setPriceChange}
            onSimulate={handleSimulate}
            isLoading={loading}
          />
          <StatsPanel results={results} />
        </main>
      </div>
    </div>
  );
}
