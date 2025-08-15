import React, { useState } from 'react';

const LyricsEditor: React.FC = () => {
  const [lyrics, setLyrics] = useState('');

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(lyrics);
    } catch (err) {
      console.error('Failed to copy lyrics:', err);
    }
  };

  const handleClear = () => setLyrics('');

  return (
    <div>
      <textarea
        value={lyrics}
        onChange={(e) => setLyrics(e.target.value)}
        rows={10}
        style={{ width: '100%' }}
      />
      <div style={{ marginTop: '8px' }}>
        <button onClick={handleCopy}>Copy</button>
        <button onClick={handleClear} style={{ marginLeft: '4px' }}>Clear</button>
      </div>
    </div>
  );
};

export default LyricsEditor;
