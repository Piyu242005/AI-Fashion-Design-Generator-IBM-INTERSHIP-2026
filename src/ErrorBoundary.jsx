import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: '', stack: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      message: error?.message || String(error) || 'Unknown frontend error',
      stack: error?.stack || '',
    };
  }

  componentDidCatch(error, info) {
    console.error('[AI Fashion Studio] Render error:', error, info);
  }

  handleReload = () => {
    try { localStorage.removeItem('ai_fashion_collections'); } catch {}
    window.location.reload();
  };

  handleClearCache = async () => {
    try {
      if ('caches' in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map(key => caches.delete(key)));
      }
      localStorage.removeItem('ai_fashion_collections');
      sessionStorage.clear();
    } catch {}
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 24, background: '#050505', color: '#fff', fontFamily: 'system-ui, sans-serif' }}>
        <section style={{ maxWidth: 620, width: '100%', padding: 28, border: '1px solid #27272a', borderRadius: 18, background: '#111113' }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>⚠️</div>
          <h1 style={{ margin: '0 0 10px', fontSize: 26 }}>AI Fashion Studio</h1>
          <p style={{ color: '#a1a1aa', lineHeight: 1.5, marginBottom: 18 }}>
            The frontend failed while rendering. The exact error is shown below so it can be diagnosed instead of hiding behind a blank screen.
          </p>
          <div style={{ padding: 14, borderRadius: 10, background: '#09090b', border: '1px solid #3f3f46', color: '#fca5a5', fontSize: 13, lineHeight: 1.5, overflowWrap: 'anywhere' }}>
            {this.state.message}
          </div>
          {this.state.stack && (
            <details style={{ marginTop: 12, color: '#71717a' }}>
              <summary style={{ cursor: 'pointer', fontSize: 12 }}>Technical details</summary>
              <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 10, overflowX: 'auto' }}>{this.state.stack}</pre>
            </details>
          )}
          <div style={{ display: 'flex', gap: 10, marginTop: 22, flexWrap: 'wrap' }}>
            <button type="button" onClick={this.handleReload} style={{ border: 0, borderRadius: 10, padding: '11px 16px', cursor: 'pointer', fontWeight: 700 }}>
              Reload & Fix
            </button>
            <button type="button" onClick={this.handleClearCache} style={{ border: '1px solid #3f3f46', borderRadius: 10, padding: '11px 16px', cursor: 'pointer', fontWeight: 700, background: '#18181b', color: '#fff' }}>
              Clear App Cache & Reload
            </button>
          </div>
        </section>
      </main>
    );
  }
}
