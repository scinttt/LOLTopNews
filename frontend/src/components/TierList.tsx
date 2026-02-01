import React from 'react';
import type { AnalysisResult } from '../services/api';

interface TierListProps {
  data: AnalysisResult;
}

const TierList: React.FC<TierListProps> = ({ data }) => {
  const tier_list = data.summary_report?.tier_list || {};

  // Ensure all tiers are present and handle empty tiers gracefully
  const tiers = ['S', 'A', 'B', 'C', 'D'];
  const fullTierList = tiers.map(tier => ({
    tier,
    champions: tier_list[tier as keyof typeof tier_list] || []
  }));

  return (
    <div className="component-tier-list">
      <h2>🏆 Tier List</h2>
      <div className="tiers-container">
        {fullTierList.map(({ tier, champions }) => (
          <div key={tier} className="tier-row">
            <div className={`tier-label tier-${tier.toLowerCase()}`}>{tier}</div>
            <div className="tier-champions">
              {champions.length > 0 ? (
                champions.map((champ: any, index: number) => (
                  <div key={index} className="champion-card">
                    <span className="champion-name">{champ.champion}</span>
                    <span className="champion-reason">{champ.reason}</span>
                  </div>
                ))
              ) : (
                <span className="no-champions">N/A</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TierList;

