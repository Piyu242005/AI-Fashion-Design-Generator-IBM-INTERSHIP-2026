import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      message: error?.message || 'An unexpected application error occurred.'
    };
  }

  componentDidCatch(error, info) {
    console.error('[AI Fashion Studio] Render error:', error, info);
  }

  handleReload = () => {
    try {
      // Remove only this app's persisted collection if it is corrupted.
      localStorage.removeItem('ai_fashion_collections');
    } catch {}
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        padding: '24px',
        background: '#050505',
        color: '#fff',
        fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
      }}>
        <section style={{ maxWidth: 520, width: '100%', textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
          <h1 style={{ fontSize: 28, margin: '0 0 10px' }}>AI Fashion Studio</h1>
          <p style={{ color: '#aaa', lineHeight: 1.6, margin: '0 0 8px' }}>
            The app encountered a temporary frontend error.
          </p>
          <p style={{ color: '#666', fontSize: 13, wordBreak: 'break-word', margin: '0 0 24px' }}>
            {this.state.message}
          </p>
          <button
            type="button"
            onClick={this.handleReload}
            style={{
              border: 0,
              borderRadius: 10,
              padding: '12px 20px',
              background: '#fff',
              color: '#000',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Reload & Fix
          </button>
        </section>
      </main>
    );
  }
}
