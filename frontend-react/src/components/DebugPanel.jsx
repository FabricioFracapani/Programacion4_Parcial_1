import { useState, useEffect } from 'react';
import { getDebugLogs, clearDebugLogs, setDebugCallback } from '../services/api';

export default function DebugPanel({ visible = true }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    setDebugCallback(setLogs);
    setLogs(getDebugLogs());
  }, []);

  function handleClear() {
    clearDebugLogs();
  }

  if (!visible) return null;

  return (
    <div className="debug-panel">
      <div className="debug-header">
        <h3>Debug Console</h3>
        <div className="debug-controls">
          <button onClick={handleClear} className="btn btn-sm btn-secondary">Limpiar</button>
        </div>
      </div>
      <div className="debug-logs">
        {logs.map((log, i) => (
          <div key={i} className={`debug-log debug-log-${log.type}`}>
            <span className="debug-time">{log.time}</span>
            <span className="debug-method">{log.method}</span>
            <span className="debug-endpoint">{log.endpoint}</span>
            {log.message && <span className="debug-msg">{log.message}</span>}
          </div>
        ))}
        {logs.length === 0 && <div className="debug-empty">Sin registros</div>}
      </div>
    </div>
  );
}
