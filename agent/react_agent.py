import re
from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from agent.tools.user_context import set_user_context
from utils.logger_hander import logger

# 正则：匹配 <think>...</think> 思考块（qwen3 模型会输出）
THINK_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL)


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
        执行 Agent 流式推理（逐 token 输出）

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

        # 使用 stream_mode="messages" 实现逐 token 流式输出
        # 每个 event 是 (message_chunk, metadata) 元组
        in_think_block = False  # 追踪是否在 <think> 块内

        for event in self.agent.stream(input_dict, stream_mode="messages", context={"report": False}):
            msg_chunk, metadata = event

            # 只处理 AI 消息（跳过 Human/Tool 消息）
            if not hasattr(msg_chunk, 'type') or msg_chunk.type != "ai":
                continue

            # 跳过工具调用消息（中间推理步骤）
            if hasattr(msg_chunk, 'tool_calls') and msg_chunk.tool_calls:
                continue
            if hasattr(msg_chunk, 'tool_call_chunks') and msg_chunk.tool_call_chunks:
                continue

            content = msg_chunk.content
            if not content:
                continue

            # ===== 过滤 <think>...</think> 思考块 =====
            # qwen3-max 模型会输出 <think>思考过程</think> 标签
            # 需要逐 chunk 处理，因为标签可能跨越多个 chunk

            # 检查是否进入 think 块
            if '<think>' in content:
                in_think_block = True
                # 保留 <think> 之前的内容
                before_think = content.split('<think>')[0]
                if before_think.strip():
                    yield before_think
                continue

            # 检查是否离开 think 块
            if '</think>' in content:
                in_think_block = False
                # 保留 </think> 之后的内容
                after_think = content.split('</think>')[-1]
                if after_think.strip():
                    yield after_think
                continue

            # 在 think 块内，跳过
            if in_think_block:
                continue

            # 正常内容，直接输出
            yield content


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
