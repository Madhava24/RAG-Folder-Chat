import React, { useState } from 'react';
import Chat from './components/Chat.jsx';
import FolderUpload from './components/FolderUpload.jsx';

export default function App() {
  const [ingestedDir, setIngestedDir] = useState(null);

  return (
    <div className="app">
      <div className="header">
        <h2 style={{margin:0}}>FolderChat Demo</h2>
        {/* <div style={{fontSize:'0.75rem', opacity:0.7}}>Backend: http://localhost:8000</div> */}
      </div>
      <FolderUpload onIngested={setIngestedDir} />
      <Chat disabled={false} />
    </div>
  );
}
