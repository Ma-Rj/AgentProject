from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from agent.tools.user_context import set_user_context
from utils.logger_hander import logger


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(
        self,
        query: str,
        user_id: int = 0,
        user_city: str = "",
        history: list[dict] = None,
        db_session=None,
    ):
        """
        执行 Agent 流式推理

        :param query: 当前用户输入
        :param user_id: 当前认证用户 ID
        :param user_city: 当前用户所在城市
        :param history: 历史消息列表 [{"role": "user/assistant", "content": "..."}]
        :param db_session: 数据库 Session（供工具查询使用）
        """
        # 设置用户上下文（供工具函数读取）
        set_user_context(user_id, user_city, db_session)

        # 构建消息列表（包含历史对话）
        messages = []

        if history:
            # 保留最近 20 条历史消息，避免 Token 超限
            recent_history = history[-20:]
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        # 添加当前用户输入
        messages.append({"role": "user", "content": query})

        input_dict = {"messages": messages}

        logger.info(f"[ReactAgent] 开始推理, user_id={user_id}, 历史消息数={len(messages) - 1}")

        # 第三个参数 context 就是上下文 runtime 中的信息，用于提示词切换标记
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


# 全局单例 Agent（避免每次请求重复初始化）
_agent_instance = None


def get_agent() -> ReactAgent:
    """获取全局 Agent 单例"""
    global _agent_instance
    if _agent_instance is None:
        logger.info("[ReactAgent] 初始化 Agent 实例...")
        _agent_instance = ReactAgent()
        logger.info("[ReactAgent] Agent 实例初始化完成")
    return _agent_instance


if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
