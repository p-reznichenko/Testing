import React from 'react';

export interface SelectedWordInfo {
  word: string;
  synonyms: string[];
  partOfSpeech?: string;
  examples?: string[];
}

interface WordInfoProps {
  selectedWordInfo: SelectedWordInfo;
}

const WordInfo: React.FC<WordInfoProps> = ({ selectedWordInfo }) => {
  const { word, synonyms, partOfSpeech, examples } = selectedWordInfo;

  return (
    <div>
      <h3>{word}</h3>
      {partOfSpeech && <p>Part of speech: {partOfSpeech}</p>}
      {synonyms.length > 0 && (
        <div>
          <strong>Synonyms:</strong>
          <ul>
            {synonyms.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
      {examples && examples.length > 0 && (
        <div>
          <strong>Examples:</strong>
          <ul>
            {examples.map((ex, i) => (
              <li key={i}>{ex}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default WordInfo;
