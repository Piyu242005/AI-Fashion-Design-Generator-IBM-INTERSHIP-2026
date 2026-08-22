import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.jsx';

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[AI Fashion Studio] Render error:', error, info);
  }

  handleReload = () => {
    try {
      // Remove only the app's potentially corrupted local data.
      localStorage.removeItem('ai_fashion_collections');
    } catch (_) {}
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24, background: '#09090b', color: '#fff', fontFamily: 'system-ui, sans-serif' }}>
        <section style={{ width: '100%', maxWidth: 560, padding: 28, border: '1px solid #27272a', borderRadius: 18, background: '#111113' }}>
          <h1 style={{ margin: '0 0 10px', fontSize: 24 }}>AI Fashion Studio</h1>
          <p style={{ margin: '0 0 18px', color: '#a1a1aa', lineHeight: 1.5 }}>
            The application encountered a temporary browser error. Your saved designs can be cleared and the application restarted safely.
          </p>
          <button onClick={this.handleReload} style={{ border: 0, borderRadius: 10, padding: '11px 16px', cursor: 'pointer', fontWeight: 700 }}>
            Reload & Fix
          </button>
          {import.meta.env.DEV && this.state.error && (
            <pre style={{ marginTop: 18, whiteSpace: 'pre-wrap', color: '#fca5a5', fontSize: 12 }}>
              {String(this.state.error?.stack || this.state.error)}
            </pre>
          )}
        </section>
      </main>
    );
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
  </React.StrictMode>
);
