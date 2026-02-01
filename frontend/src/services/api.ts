/**
 * LOL Top Lane Guide - API 服务
 * 与后端 FastAPI 交互
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalysisResult {
  version: string;
  top_lane_changes: any[];
  impact_analyses: any[] | null;
  summary_report: any | null;
  metadata: any;
}

/**
 * 分析指定版本的更新公告
 * @param version 版本号，默认为 "latest"
 * @returns 分析结果
 */
export async function analyzeVersion(version: string = 'latest'): Promise<AnalysisResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze?version=${version}`);

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
