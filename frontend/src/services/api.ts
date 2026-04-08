/**
 * LOL Top Lane Guide - API 服务
 * 与后端 FastAPI 交互
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface AnalysisResult {
  version: string;
  top_lane_changes: any[];
  impact_analyses: any[] | null;
  summary_report: any | null;
  metadata: any;
}

export interface VersionEntry {
  version: string;
  analyzed_at: string;
}

export interface VersionsIndex {
  latest: string | null;
  versions: VersionEntry[];
}

/**
 * 分析指定版本的更新公告
 * @param version 版本号，默认为 "latest"
 * @returns 分析结果
 */
export async function analyzeVersion(version: string = 'latest'): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze?version=${version}`);

    if (!response.ok) {
      throw new Error(`API 请求失败: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('分析版本失败:', error);
    throw error;
  }
}

/**
 * 使用 POST 方式分析（可提供内容）
 * @param version 版本号
 * @param rawContent 原始内容（可选）
 * @returns 分析结果
 */
export async function analyzeVersionPost(
  version: string = 'latest',
  rawContent?: string
): Promise<AnalysisResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        version,
        raw_content: rawContent,
      }),
    });

    if (!response.ok) {
      throw new Error(`API 请求失败: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('分析版本失败:', error);
    throw error;
  }
}

/**
 * Fetch the version index (latest + history)
 */
export async function fetchVersions(): Promise<VersionsIndex> {
  const response = await fetch(`${API_BASE_URL}/api/versions`);
  if (!response.ok) {
    throw new Error(`Failed to fetch versions: ${response.status}`);
  }
  return response.json();
}

/**
 * Fetch cached analysis for a specific version
 */
export async function fetchVersionData(version: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/versions/${version}`);
  if (!response.ok) {
    throw new Error(`Version ${version} not found`);
  }
  return response.json();
}

/**
 * Subscribe an email to patch notifications
 */
export async function subscribe(email: string): Promise<{ ok: boolean; email: string; action: string }> {
  const response = await fetch(`${API_BASE_URL}/api/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Subscribe failed: ${response.status}`);
  }
  return response.json();
}

/**
 * Trigger background backfill of recent versions
 */
export async function triggerBackfill(): Promise<void> {
  await fetch(`${API_BASE_URL}/api/backfill`, { method: 'POST' });
}

/**
 * 健康检查
 * @returns 健康状态
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error('健康检查失败:', error);
    throw error;
  }
}
