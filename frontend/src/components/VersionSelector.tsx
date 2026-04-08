import React from 'react';
import type { VersionEntry } from '../services/api';

interface VersionSelectorProps {
  versions: VersionEntry[];
  currentVersion: string | null;
  onSelect: (version: string) => void;
}

const VersionSelector: React.FC<VersionSelectorProps> = ({ versions, currentVersion, onSelect }) => {
  if (versions.length === 0) {
    return null;
  }

  return (
    <div className="version-selector">
      <span className="version-selector-label">History:</span>
      <div className="version-selector-list">
        {versions.map((entry) => (
          <button
            key={entry.version}
            className={`version-selector-item ${entry.version === currentVersion ? 'active' : ''}`}
            onClick={() => onSelect(entry.version)}
            title={`Analyzed: ${new Date(entry.analyzed_at).toLocaleDateString()}`}
          >
            v{entry.version}
          </button>
        ))}
      </div>
    </div>
  );
};

export default VersionSelector;
