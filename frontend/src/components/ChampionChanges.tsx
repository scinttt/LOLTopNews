import React from 'react';
import type { AnalysisResult } from '../services/api';

interface ChampionChangesProps {
  data: AnalysisResult;
}

const ChampionChanges: React.FC<ChampionChangesProps> = ({ data }) => {
  const championChanges = data.top_lane_changes.filter(change => change.type === 'champion');
  const totalChanges = data.top_lane_changes.length;

  const getChangeSymbol = (type: string) => {
    if (type === 'buff') return '⬆️';
    if (type === 'nerf') return '⬇️';
    return '🔄';
  };

  const getRelevanceLabel = (relevance: string) => {
    return relevance === 'primary' ? '主流' : '冷门';
  };

  return (
    <div className="component-champion-changes">
      <h2>🦸 英雄变更 ({totalChanges} 个)</h2>
      <div className="changes-container">
        {championChanges.map((change, index) => (
          <div key={index} className="change-item">
            <span className="change-symbol">{getChangeSymbol(change.change_type || 'adjust')}</span>
            <span className="change-name">{change.champion}</span>
            <span className="change-relevance">{getRelevanceLabel(change.relevance || 'secondary')}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChampionChanges;


