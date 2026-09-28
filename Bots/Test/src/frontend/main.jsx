import React from 'react';
import ReactDOM from 'react-dom/client';

const App = () => (
  <div style={{ padding: '2rem', textAlign: 'center', fontFamily: 'sans-serif' }}>
    <h1>Backend testi</h1>
    <p>Express server listening on port 3000</p>
    <p>Lisää frontend koodi tähän.</p>
  </div>
);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);