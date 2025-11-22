import React, { useState } from 'react';
import { ingestPath } from '../api.js';

export default function FolderUpload({ onIngested }) {
  const [path, setPath] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleIngest() {
    const dir = path.trim();
    if (!dir) return;
    setLoading(true);
    setStatus('Ingesting path...');
    try {
      const res = await ingestPath(dir);
      setStatus(res.message + ' (' + res.chunks_indexed + ')');
      onIngested?.(res.input_dir);
    } catch (err) {
      setStatus('Ingestion failed: ' + (err.response?.data?.detail || err.message || 'error'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="upload-box">
      <p style={{marginTop:0}}>Enter server-accessible folder path to ingest:</p>
      <input
        type="text"
        placeholder="e.g. C:/data/docs or ./data"
        value={path}
        onChange={e => setPath(e.target.value)}
        disabled={loading}
        style={{width:'100%', marginBottom:'0.5rem', padding:'0.5rem', borderRadius:'6px', border:'1px solid #444', background:'#121417', color:'#fff'}}
      />
      <button onClick={handleIngest} disabled={loading || !path}>Ingest Folder</button>
      {status && <div style={{marginTop:'0.5rem', fontSize:'0.8rem'}}>{status}</div>}
    </div>
  );
}
