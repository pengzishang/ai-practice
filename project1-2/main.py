import autogen
from pathlib import Path
import sys
import asyncio
import subprocess

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
from config.settings import Settings

settings = Settings()


async def start_services():
    """启动模拟服务"""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.fastapi:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    process = subprocess.Popen(cmd, cwd=str(project_root))
    await asyncio.sleep(3)
    return process


async def run_agents():
    """运行 autogen 智能体"""
    config_list = [
        {
            "model": settings.autogen_model,
            "api_key": settings.autogen_api_key,
            "base_url": settings.autogen_base_url,
            # AutoGen 内置价格表不包含 deepseek-v4-flash 等自定义模型时，
            # 需要显式提供价格，否则会打印 “Model ... is not found” warning。
            # 格式为：[prompt_price_per_1k, completion_token_price_per_1k]
            # 这里设为 0 表示不统计费用；如需准确成本，可改成服务商实际价格。
            "price": [0.001, 0.002],
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": settings.autogen_temperature,
        "timeout": settings.autogen_timeout,
    }

    # ============================================================
    # 主持人：不点名，只负责最后总结
    # ============================================================
    moderator = autogen.AssistantAgent(
        name="主持人",
        llm_config=llm_config,
        system_message="""你是这场辩论的主持人。
    你只有两个任务：
    1. 开场：简单介绍议题，宣布"开始自由辩论"，然后不要插话
    2. 收场：当被叫到时，汇总所有观点，给出最终结论
    最终总结格式：
    【主持人 - 最终结论】
    1. 核心结论（一句话）
    2. 主要事实依据
    3. 主要风险
    4. 主要机会  
    5. 创新建议
    6. 最终建议：做 / 不做 / 有条件做
    总结完毕后必须输出 TERMINATE。
    注意：除了开场和总结，你不发表任何个人观点。""",
    )
    # ============================================================
    # 6个思考帽：去掉所有"等待点名"的限制
    # 可以自由回应任何人，保持角色立场即可
    # ============================================================
    bai_xi = autogen.AssistantAgent(
        name="白析",
        llm_config=llm_config,
        system_message="""你是"白析"，白帽思维，事实分析师。
    自由辩论，无需等待点名。
    只从事实、数据、定义角度发言，可以纠正其他人的错误事实。
    发言简洁，100字以内，开头写【白析】。""",
    )
    hong_gan = autogen.AssistantAgent(
        name="红感",
        llm_config=llm_config,
        system_message="""你是"红感"，红帽思维，情绪观察者。
    自由辩论，无需等待点名。
    只从情绪、直觉、用户心理角度发言，不需要数据支撑。
    发言简洁，100字以内，开头写【红感】。""",
    )
    mo_jing = autogen.AssistantAgent(
        name="墨警",
        llm_config=llm_config,
        system_message="""你是"墨警"，黑帽思维，风险审查官。
    自由辩论，无需等待点名。
    只从风险、漏洞、失败场景角度发言，爱反驳曜成的乐观。
    发言简洁，100字以内，开头写【墨警】。""",
    )
    yao_cheng = autogen.AssistantAgent(
        name="曜成",
        llm_config=llm_config,
        system_message="""你是"曜成"，黄帽思维，价值发现者。
    自由辩论，无需等待点名。
    只从价值、机会、收益角度发言，爱反驳墨警的悲观。
    发言简洁，100字以内，开头写【曜成】。""",
    )
    qing_chuang = autogen.AssistantAgent(
        name="青创",
        llm_config=llm_config,
        system_message="""你是"青创"，绿帽思维，创意探索者。
    自由辩论，无需等待点名。
    只提创新方案和替代路径，专门在别人说"不行"时说"换个思路试试"。
    发言简洁，100字以内，开头写【青创】。""",
    )
    lan_chou = autogen.AssistantAgent(
        name="蓝筹",
        llm_config=llm_config,
        system_message="""你是"蓝筹"，蓝帽思维，流程控制者。
    自由辩论，无需等待点名。
    负责在辩论跑偏时拉回主题，提醒大家讨论焦点。
    发言简洁，100字以内，开头写【蓝筹】。
    不做最终总结，那是主持人的工作。""",
    )
    user_proxy = autogen.UserProxyAgent(
        name="客户",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    agents = [bai_xi,hong_gan,lan_chou,qing_chuang,yao_cheng,mo_jing,moderator]
    groupchat = autogen.GroupChat(agents,messages=[],max_round=settings.max_round,speaker_selection_method='auto')
    manager = autogen.GroupChatManager(groupchat,llm_config=llm_config)

    user_proxy.initiate_chat(manager, message="全球变暖是否对每个普通家庭有影响?")


async def main():
    """主函数"""
    global _process
    _process = await start_services()
    try:
        await run_agents()
    finally:
        _cleanup()


_process = None


def _cleanup():
    if _process:
        _process.terminate()


if __name__ == "__main__":
    import asyncio
    import atexit

    atexit.register(_cleanup)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _cleanup()
