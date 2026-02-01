import React from 'react';
import type { AnalysisResult } from '../services/api';

interface ImpactAnalysisProps {
  data: AnalysisResult;
}

const ImpactAnalysis: React.FC<ImpactAnalysisProps> = ({ data }) => {
  const champion_analyses = data.impact_analyses?.[0]?.champion_analyses || [];

  const getChangeSymbol = (type: string) => {
    if (type === 'buff') return '⬆️';
    if (type === 'nerf') return '⬇️';
    return '🔄';
  };

  if (champion_analyses.length === 0) {
    return (
      <div className="component-impact-analysis">
        <h2>📈 影响分析</h2>
        <p>暂无影响分析数据</p>
      </div>
    );
  }

  return (
    <div className="component-impact-analysis">
      <h2>📈 影响分析</h2>
      {champion_analyses.map((analysis: any, index: number) => (
        <div key={index} className="analysis-card">
          <h3>
            {getChangeSymbol(analysis.change_type)} {analysis.champion}
          </h3>
          <div className="analysis-section">
            <h4>Gameplay Changes:</h4>
            <p><strong>Laning:</strong> {analysis.gameplay_changes?.laning_phase || 'N/A'}</p>
            <p><strong>Teamfight:</strong> {analysis.gameplay_changes?.teamfight_role || 'N/A'}</p>
            <p><strong>Build:</strong> {analysis.gameplay_changes?.build_adjustment || 'N/A'}</p>
          </div>
          <div className="analysis-section">
            <h4>Meta Impact:</h4>
            <p><strong>Tier:</strong> {analysis.meta_impact?.tier_prediction || 'N/A'} ({analysis.meta_impact?.tier_change || 'N/A'})</p>
            <p><strong>Counters:</strong> {analysis.meta_impact?.counter_changes?.join(', ') || 'N/A'}</p>
            <p><strong>Synergy Items:</strong> {analysis.meta_impact?.synergy_items?.join(', ') || 'N/A'}</p>
          </div>
          <div className="analysis-section">
            <h4>Overall Assessment:</h4>
            <div className="assessment-details">
                <p><strong>Strength Score:</strong> <span className="strength-score">{analysis.overall_assessment?.strength_score || 'N/A'}/10</span></p>
                <p><strong>Win Rate Trend:</strong> {analysis.overall_assessment?.win_rate_trend || 'N/A'}</p>
                <p><strong>Worth Practicing:</strong> {analysis.overall_assessment?.worth_practicing ? 'Yes' : 'No'}</p>
            </div>
            <p className="reasoning">"{analysis.overall_assessment?.reasoning || 'N/A'}"</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ImpactAnalysis;

