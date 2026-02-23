import React, { useState, useEffect } from 'react';
import ChampionChanges from './components/ChampionChanges';
import ImpactAnalysis from './components/ImpactAnalysis';
import Summary from './components/Summary';
import TierList from './components/TierList';
import { analyzeVersion, type AnalysisResult } from './services/api';

const App: React.FC = () => {
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState('latest');

  // 加载数据
  const loadData = async (versionToLoad: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await analyzeVersion(versionToLoad);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
      console.error('加载数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadData(version);
  }, []);

  // Validate version format before submitting: accept "latest" or "X.Y" / "X.YY"
  const isVersionInputValid = (input: string): boolean => {
    const trimmed = input.trim();
    return trimmed === 'latest' || /^\d+\.\d+$/.test(trimmed);
  };

  // 重新分析
  const handleAnalyze = () => {
    const trimmedVersion = version.trim();
    if (!isVersionInputValid(trimmedVersion)) {
      setError('版本号格式错误，请输入 "latest" 或如 "26.3"、"15.24" 格式的版本号');
      return;
    }
    loadData(trimmedVersion);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>LOL Top Lane Guide - Patch {data?.version || version}</h1>
        <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <input
            type="text"
            value={version}
            onChange={(e) => { setVersion(e.target.value); setError(null); }}
            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
            placeholder="输入版本号 (如 26.3 或 latest)"
            style={{
              padding: '0.5rem',
              fontSize: '1rem',
              minWidth: '200px',
              borderColor: version && !isVersionInputValid(version) ? 'red' : undefined,
            }}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{ padding: '0.5rem 1rem', fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer' }}
          >
            {loading ? '分析中...' : '开始分析'}
          </button>
        </div>
      </header>

      <main>
        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p>正在分析版本 {version}，请稍候...</p>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              这可能需要几分钟时间，因为需要爬取数据并进行 AI 分析
            </p>
          </div>
        )}

        {error && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'red' }}>
            <p>❌ 错误: {error}</p>
            <button onClick={handleAnalyze} style={{ marginTop: '1rem', padding: '0.5rem 1rem' }}>
              重试
            </button>
          </div>
        )}

        {!loading && !error && data && (
          <>
            <Summary data={data} />
            <TierList data={data} />
            <ChampionChanges data={data} />
            <ImpactAnalysis data={data} />
          </>
        )}
      </main>
    </div>
  );
};

export default App;