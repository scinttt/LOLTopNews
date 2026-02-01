import React from 'react';
import type { AnalysisResult } from '../services/api';

interface SummaryProps {
  data: AnalysisResult;
}

const Summary: React.FC<SummaryProps> = ({ data }) => {
  const executive_summary = data.summary_report?.executive_summary || '总结报告生成中...';

  return (
    <div className="component-summary">
      <h2>📝 总结报告</h2>
      <p>{executive_summary}</p>
    </div>
  );
};

export default Summary;

