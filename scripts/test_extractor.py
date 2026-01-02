"""
测试 Extractor Node
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.workflow import run_workflow


async def test_with_sample_data():
    """使用示例数据测试"""
    print("=" * 70)
    print("测试 Extractor Node - 示例数据")
    print("=" * 70)

    # 读取示例数据
    sample_file = "data/sample_patch_14.24.txt"

    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✅ 读取示例数据: {len(content)} 字符\n")

        # 运行工作流（目前只有 Extractor 实现）
        result = await run_workflow(content, version="14.24")

        # 显示结果
        changes = result.get("top_lane_changes", [])
        print(f"✅ Extractor 完成")
        print(f"\n提取结果:")
        print(f"   版本号: {result.get('version')}")
        print(f"   上单相关变更: {len(changes)} 个")

        # 按类型分组显示
        champions = [c for c in changes if c["type"] == "champion"]
        items = [c for c in changes if c["type"] == "item"]
        systems = [c for c in changes if c["type"] == "system"]

        print(f"\n   - 英雄变更: {len(champions)} 个")
        for i, change in enumerate(champions[:5], 1):
            print(f"      {i}. {change['champion']} ({change['change_type']})")

        print(f"\n   - 装备变更: {len(items)} 个")
        for i, item in enumerate(items[:5], 1):
            print(f"      {i}. {item['item']}")

        print(f"\n   - 系统变更: {len(systems)} 个")
        for i, sys in enumerate(systems[:5], 1):
            print(f"      {i}. {sys['category']}")

        # Token 使用
        metadata = result.get("metadata", {})
        if "extractor_tokens" in metadata:
            tokens = metadata["extractor_tokens"]
            print(f"\n   Token 使用:")
            print(f"      输入: {tokens.get('prompt_tokens', 0)}")
            print(f"      输出: {tokens.get('completion_tokens', 0)}")
            print(f"      总计: {tokens.get('total_tokens', 0)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_real_data():
    """使用真实数据测试"""
    print("\n" + "=" * 70)
    print("测试 Extractor Node - 真实数据")
    print("=" * 70)

    real_file = "data/raw_patches/latest_real.txt"

    if not os.path.exists(real_file):
        print(f"⚠️ 真实数据文件不存在: {real_file}")
        print(f"   跳过此测试")
        return None

    try:
        with open(real_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✅ 读取真实数据: {len(content)} 字符\n")

        # 运行工作流
        result = await run_workflow(content, version="15.24")

        # 显示结果
        changes = result.get("top_lane_changes", [])
        print(f"✅ Extractor 完成")
        print(f"\n提取结果:")
        print(f"   版本号: {result.get('version')}")
        print(f"   上单相关变更: {len(changes)} 个")

        # 显示一些变更
        champions = [c for c in changes if c["type"] == "champion"]
        if champions:
            print(f"\n   英雄变更示例:")
            for i, change in enumerate(champions[:3], 1):
                print(f"      {i}. {change['champion']} ({change['change_type']})")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行测试"""
    print("\n" + "=" * 70)
    print("Extractor Node 测试套件")
    print("=" * 70 + "\n")

    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_deepseek_api_key_here":
        print("❌ 错误: DEEPSEEK_API_KEY 未配置")
        return

    # 运行测试
    results = []
    results.append(("示例数据", await test_with_sample_data()))

    real_result = await test_with_real_data()
    if real_result is not None:
        results.append(("真实数据", real_result))

    # 汇总
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 通过")

    if success_count == total_count:
        print("\n✅ Extractor Node 测试通过！")
        print("\n📝 下一步:")
        print("   - Day 4-5: 实现 Analyzer Node")
        print("   - Day 8: 实现 Summarizer Node")
    else:
        print("\n❌ 部分测试失败")

    print()


if __name__ == "__main__":
    asyncio.run(main())
