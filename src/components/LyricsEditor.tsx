import React, { useState } from 'react';

// Fetch synonyms or meanings for a given word using the Datamuse API.
// Returns an array of related words or an empty array on failure.
export const fetchWordInfo = async (word: string): Promise<string[]> => {
  try {
    const response = await fetch(`https://api.datamuse.com/words?ml=${word}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    return data.map((item: { word: string }) => item.word);
  } catch (err) {
    console.error('Failed to fetch word info:', err);
    return [];
  }
};

const LyricsEditor: React.FC = () => {
  const [lyrics, setLyrics] = useState('');
  const [selectedWordInfo, setSelectedWordInfo] = useState<string[]>([]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(lyrics);
    } catch (err) {
      console.error('Failed to copy lyrics:', err);
    }
  };

  const handleClear = () => setLyrics('');

  const handleMouseUp = async (
    e: React.MouseEvent<HTMLTextAreaElement, MouseEvent>
  ) => {
    const { selectionStart, selectionEnd, value } = e.currentTarget;
    const selected = value
      .substring(selectionStart, selectionEnd)
      .trim();
    // Only fetch info if a single word is selected
    if (selected && !/\s/.test(selected)) {
      const info = await fetchWordInfo(selected);
      setSelectedWordInfo(info);
    } else {
      setSelectedWordInfo([]);
    }
  };

  return (
    <div>
      <textarea
        value={lyrics}
        onChange={(e) => setLyrics(e.target.value)}
        onMouseUp={handleMouseUp}
        rows={10}
        style={{ width: '100%' }}
      />
      <div style={{ marginTop: '8px' }}>
        <button onClick={handleCopy}>Copy</button>
        <button onClick={handleClear} style={{ marginLeft: '4px' }}>Clear</button>
      </div>
      {selectedWordInfo.length > 0 && (
        <ul>
          {selectedWordInfo.map((word, index) => (
            <li key={index}>{word}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default LyricsEditor;
