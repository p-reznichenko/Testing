import React, { useState } from 'react';
import WordInfo, { SelectedWordInfo } from './WordInfo';

// Fetch synonyms and additional info for a given word using the Datamuse API.
// Returns an object with word details or null on failure.
export const fetchWordInfo = async (
  word: string
): Promise<SelectedWordInfo | null> => {
  try {
    const [synRes, detailRes] = await Promise.all([
      fetch(`https://api.datamuse.com/words?ml=${word}`),
      fetch(`https://api.datamuse.com/words?sp=${word}&md=d,p&max=1`),
    ]);

    if (!synRes.ok || !detailRes.ok) {
      throw new Error('Network response was not ok');
    }

    const synonymsData = await synRes.json();
    const detailsData = await detailRes.json();

    const synonyms = synonymsData.map((item: { word: string }) => item.word);

    let partOfSpeech: string | undefined;
    let examples: string[] = [];

    if (detailsData.length > 0) {
      const details = detailsData[0];
      if (details.tags) {
        const posTag = details.tags.find((tag: string) =>
          ['n', 'v', 'adj', 'adv'].includes(tag)
        );
        const map: Record<string, string> = {
          n: 'noun',
          v: 'verb',
          adj: 'adjective',
          adv: 'adverb',
        };
        partOfSpeech = posTag ? map[posTag] || posTag : undefined;
      }

      if (details.defs) {
        examples = details.defs.map((def: string) => def.split('\t')[1]);
      }
    }

    return { word, synonyms, partOfSpeech, examples };
  } catch (err) {
    console.error('Failed to fetch word info:', err);
    return null;
  }
};

const LyricsEditor: React.FC = () => {
  const [lyrics, setLyrics] = useState('');
  const [selectedWordInfo, setSelectedWordInfo] =
    useState<SelectedWordInfo | null>(null);

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
      setSelectedWordInfo(null);
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
      {selectedWordInfo && <WordInfo selectedWordInfo={selectedWordInfo} />}
    </div>
  );
};

export default LyricsEditor;
