import React, { useState, useEffect } from 'react';
import ChampionChanges from './components/ChampionChanges';
import ImpactAnalysis from './components/ImpactAnalysis';
import SubscribeForm from './components/SubscribeForm';
import Summary from './components/Summary';
import TierList from './components/TierList';
import VersionSelector from './components/VersionSelector';
import {
  analyzeVersion,
  fetchVersions,
  fetchVersionData,
  triggerBackfill,
  type AnalysisResult,
  type VersionEntry,
} from './services/api';

const App: React.FC = () => {
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState('');
  const [versions, setVersions] = useState<VersionEntry[]>([]);
  const [currentVersion, setCurrentVersion] = useState<string | null>(null);

  // Refresh the version list from backend
  const refreshVersions = async () => {
    try {
      const index = await fetchVersions();
      setVersions(index.versions);
    } catch { /* ignore */ }
  };

  // On mount: load latest cached version, or auto-analyze latest
  useEffect(() => {
    (async () => {
      try {
        const index = await fetchVersions();
        setVersions(index.versions);

        if (index.latest) {
          // Cache exists — load instantly
          const result = await fetchVersionData(index.latest);
          setData(result);
          setCurrentVersion(index.latest);
          setVersion(index.latest);
          // Backfill older versions in the background
          triggerBackfill();
        } else {
          // No cache — auto-analyze latest version
          const result = await analyzeVersion('latest');
          setData(result);
          setCurrentVersion(result.version);
          setVersion(result.version);
          await refreshVersions();
          // Backfill previous versions in the background
          triggerBackfill();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Periodically refresh version list while backfill runs
  useEffect(() => {
    if (!data) return;
    const interval = setInterval(refreshVersions, 15000);
    // Stop polling after 5 minutes (backfill should be done)
    const timeout = setTimeout(() => clearInterval(interval), 300000);
    return () => { clearInterval(interval); clearTimeout(timeout); };
  }, [data]);

  // Trigger a new analysis (crawl + LLM pipeline)
  const handleAnalyze = async () => {
    const trimmedVersion = version.trim() || 'latest';
    if (!isVersionInputValid(trimmedVersion)) {
      setError('版本号格式错误，请输入 "latest" 或如 "26.3"、"15.24" 格式的版本号');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await analyzeVersion(trimmedVersion);
      setData(result);
      setCurrentVersion(result.version);
      await refreshVersions();
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setLoading(false);
    }
  };

  // Switch to a previously cached version (instant)
  const handleVersionSelect = async (ver: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchVersionData(ver);
      setData(result);
      setCurrentVersion(ver);
      setVersion(ver);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const isVersionInputValid = (input: string): boolean => {
    const trimmed = input.trim();
    return trimmed === 'latest' || /^\d+\.\d+$/.test(trimmed);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>LOL Top Lane Guide - Patch {currentVersion || '...'}</h1>
        <VersionSelector
          versions={versions}
          currentVersion={currentVersion}
          onSelect={handleVersionSelect}
        />
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
            <p>正在分析最新版本，请稍候...</p>
            <p style={{ fontSize: '0.9rem', color: '#888' }}>
              首次分析需要爬取数据并进行 AI 分析，大约需要 1-2 分钟
            </p>
          </div>
        )}

        {error && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'red' }}>
            <p>错误: {error}</p>
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
            <SubscribeForm />
          </>
        )}
      </main>
    </div>
  );
};

export default App;
