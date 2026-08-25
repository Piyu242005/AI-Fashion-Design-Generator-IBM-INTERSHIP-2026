import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import ErrorBoundary from './ErrorBoundary.jsx';
import FeatureHub from './FeatureHub.jsx';
import MissUniverseGallery from './MissUniverseGallery.jsx';
import MissUniverseNav from './MissUniverseNav.jsx';

function repairPersistedState() {
  try {
    const raw = localStorage.getItem('ai_fashion_collections');
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error('Invalid collections format');
  } catch (error) {
    console.warn('[AI Fashion Studio] Resetting invalid local storage:', error);
    try { localStorage.removeItem('ai_fashion_collections'); } catch {}
  }
}

repairPersistedState();

const root = document.getElementById('root');
if (!root) throw new Error('Missing #root element');

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
      <FeatureHub />
      <MissUniverseGallery />
      <MissUniverseNav />
    </ErrorBoundary>
  </React.StrictMode>
);
