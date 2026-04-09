import os
from datetime import datetime
from utils.logger_hander import logger
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from agent.tools.user_context import get_user_id_from_context, get_user_city_from_context, get_db_session_from_context
from dotenv import load_dotenv
import httpx

load_dotenv()

rag = RagSummarizeService()

# 天气 API 配置
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_PROVIDER = os.getenv("WEATHER_API_PROVIDER", "weatherapi")


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city: str) -> str:
    """
    调用 weatherapi.com 真实天气 API
    获取指定城市的实时天气信息
    """
    if not WEATHER_API_KEY:
        logger.warning("[get_weather] 未配置 WEATHER_API_KEY，返回默认天气")
        return f"城市{city}天气信息暂时无法获取（API Key 未配置）"

    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": city,
            "lang": "zh",
        }

        with httpx.Client(timeout=10) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        current = data.get("current", {})
        location = data.get("location", {})

        weather_info = (
            f"城市：{location.get('name', city)}（{location.get('region', '')}）\n"
            f"天气状况：{current.get('condition', {}).get('text', '未知')}\n"
            f"温度：{current.get('temp_c', '--')}°C（体感温度：{current.get('feelslike_c', '--')}°C）\n"
            f"空气湿度：{current.get('humidity', '--')}%\n"
            f"风况：{current.get('wind_dir', '')}风 {current.get('wind_kph', '--')}km/h\n"
            f"空气质量指数(AQI)：{current.get('air_quality', {}).get('pm2_5', '暂无数据')}\n"
            f"紫外线指数：{current.get('uv', '--')}\n"
            f"降水量：{current.get('precip_mm', 0)}mm"
        )

        logger.info(f"[get_weather] 成功获取 {city} 天气")
        return weather_info

    except httpx.HTTPStatusError as e:
        logger.error(f"[get_weather] API 请求失败: {e.response.status_code}")
        return f"获取{city}天气信息失败，请稍后重试"
    except Exception as e:
        logger.error(f"[get_weather] 获取天气异常: {str(e)}", exc_info=True)
        return f"获取{city}天气信息失败: {str(e)}"


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    """从当前认证用户的数据库记录中获取城市"""
    city = get_user_city_from_context()
    if city:
        logger.info(f"[get_user_location] 获取用户城市: {city}")
        return city
    return "用户未设置所在城市，请先在个人设置中设置城市信息"


@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    """从当前认证用户上下文中获取真实用户 ID"""
    user_id = get_user_id_from_context()
    if user_id > 0:
        logger.info(f"[get_user_id] 获取用户 ID: {user_id}")
        return str(user_id)
    return "无法获取用户ID，用户未登录"


@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    """使用系统时间获取当前月份"""
    current_month = datetime.now().strftime("%Y-%m")
    logger.info(f"[get_current_month] 当前月份: {current_month}")
    return current_month


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回，如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    """
    从 MySQL 数据库查询设备使用记录
    替代原来的 CSV 文件解析
    """
    db = get_db_session_from_context()
    if db is None:
        logger.error("[fetch_external_data] 无法获取数据库 Session")
        return ""

    try:
        from db.crud import get_device_record
        record = get_device_record(db, int(user_id), month)

        if record is None:
            logger.warning(f"[fetch_external_data] 未找到用户 {user_id} 在 {month} 的记录")
            return ""

        result = (
            f"用户ID: {user_id}\n"
            f"月份: {month}\n"
            f"用户特征: {record.feature}\n"
            f"清洁效率: {record.efficiency}\n"
            f"耗材状态: {record.consumables}\n"
            f"使用对比: {record.comparison}"
        )

        logger.info(f"[fetch_external_data] 成功检索用户 {user_id} 在 {month} 的使用记录")
        return result

    except Exception as e:
        logger.error(f"[fetch_external_data] 查询失败: {str(e)}", exc_info=True)
        return ""


@tool(description="调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"
