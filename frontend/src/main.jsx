import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

const rootEl = document.getElementById('root');

function showFatal(message) {
  if (!rootEl) return;
  rootEl.innerHTML = `
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px;font-family:system-ui,sans-serif;background:#e8eef6;color:#0f172a;text-align:center">
      <div style="max-width:28rem">
        <div style="width:64px;height:64px;margin:0 auto 12px;border-radius:14px;background:linear-gradient(135deg,#0b1f3a,#0f766e);color:#fff;display:grid;place-items:center;font:700 28px Georgia,serif">S</div>
        <h1 style="margin:0 0 8px;font-size:1.4rem">SANGAM failed to load</h1>
        <p style="margin:0;color:#475569;font-size:0.95rem">${message}</p>
        <p style="margin:16px 0 0;font-size:0.85rem;color:#64748b">
          Open via the running website (e.g. <code>http://localhost:8100</code>), not by double-clicking the HTML file.
        </p>
      </div>
    </div>
  `;
}

try {
  if (!rootEl) {
    throw new Error('Missing #root element in index.html');
  }
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} catch (err) {
  console.error(err);
  showFatal(err?.message || 'Unknown startup error');
}
