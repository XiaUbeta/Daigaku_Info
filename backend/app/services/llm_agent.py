import json
from openai import OpenAI
from app.core.config import settings

class SingleAgentPipeline:
    def __init__(self):
        # Configure client to support both standard OpenAI and compatible endpoints
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
        }
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
            
        self.client = OpenAI(**client_kwargs)
        # 使用 Siliconflow 提供的确切模型名称
        self.model = "deepseek-ai/DeepSeek-V4-Pro" if settings.OPENAI_BASE_URL else "gpt-4o-mini"

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1, # 低温度保证结构化输出的稳定性
            "response_format": {"type": "json_object"}, # 强制模型返回 JSON
            "timeout": 180.0, # 增加到 180 秒，防止大模型长上下文超时
        }
        
        import time
        for attempt in range(2):
            try:
                print(f"  [LLM] Calling {self.model} (Attempt {attempt+1}/2)...")
                response = self.client.chat.completions.create(**kwargs)
                raw_content = response.choices[0].message.content.strip()
                print(f"  [LLM Debug] Raw Response:\n{raw_content}\n" + "-"*40)
                return raw_content
            except Exception as e:
                print(f"  [LLM] Error: {e}")
                if attempt == 1:
                    return "{}"
                print("  [LLM] Retrying in 3 seconds...")
                time.sleep(3)

    def navigator_agent(self, list_page_markdown: str, max_links: int = 15) -> dict:
        """
        Takes the markdown of a news list page and extracts relevant news links.
        """
        system_prompt = f"""
        你是一个专门为【2027年入学的日本私费外国留学生】寻找升学情报的网页导航助手。
        以下是一个大学官网的新闻列表页或入试首页的文本（转换为Markdown格式，包含大量链接）。
        
        你的任务是：找出所有可能属于“入试通知”、“学部募集”、“留学生考试”、“Open Campus”等与考学直接相关的文章链接。
        忽略无关日常新闻（如教授获奖、社团活动、放假通知），以及不符合时间的新闻。
        
        请严格输出 JSON 格式，包含一个名为 `urls` 的数组，数组中每个元素是一个对象，包含 `title` 和 `url`。
        最多提取 {max_links} 个最重要的链接。
        {{
            "urls": [
                {{"title": "文章标题", "url": "链接地址"}}
            ]
        }}
        确保返回的数据可以直接被 json.loads 解析。
        """
        
        # 截断以防止超出 token 限制
        truncated_markdown = list_page_markdown[:20000]
        result_str = self._call_llm(system_prompt, truncated_markdown)
        try:
            if result_str.startswith("```json"):
                result_str = result_str.replace("```json\n", "").replace("```", "").strip()
            data = json.loads(result_str)
            return data.get("urls", [])
        except json.JSONDecodeError:
            print(f"  [LLM Navigator] JSON Decode Error. Raw output: {result_str}")
            return []

    def process_news(self, raw_text: str) -> dict:
        """
        The upgraded single-shot pipeline using DeepSeek for structured output.
        """
        system_prompt = """
        你是一个专门为【日本私费外国留学生（学部考学）】筛选并提取升学情报的专家。
        阅读用户提供的日文网页文本，首先判断其是否对外国留学生考学部有价值（比如留学生入试出愿、制度变更、Open Campus等；排除国内高中生常规入试、大学院入试、日常无关新闻）。
        
        请严格输出 JSON 格式，包含以下字段：
        {
            "is_relevant": true 或 false,
            "category": "出愿情报" | "制度变更" | "Open Campus" | "讲座" | "合格发表" | "其他",
            "published_at": "YYYY/MM/DD", // 提取新闻发布日期。如果网页中完全没写日期，请填写"不明"
            "target_faculties": ["学部名1", "学部名2"], // 若全校通用填 ["全学部"]
            "timeline": [
                {"event_name": "事件名称(如出願開始)", "date_str": "YYYY/MM/DD", "is_deadline": true 或 false}
            ],
            "exam_requirements": {"EJU": "...", "TOEFL": "..."}, // 提取考试要求，若无则填 {}
            "summary": "一句话中文极简摘要，不超过50字",
            "important_dates_text": "将提取的时间线整理成一段简练的中文文本说明（用于兼容前端展示）"
        }
        确保返回的数据可以直接被 json.loads 解析，不要包含任何 markdown 代码块标记。
        """
        
        result_str = self._call_llm(system_prompt, raw_text)
        try:
            # Clean up potential markdown formatting just in case
            if result_str.startswith("```json"):
                result_str = result_str.replace("```json\n", "").replace("```", "").strip()
            data = json.loads(result_str)
            return data
        except json.JSONDecodeError:
            print(f"  [LLM] JSON Decode Error. Raw output: {result_str}")
            return None

# Replace old MultiAgentPipeline with the new SingleAgentPipeline
llm_pipeline = SingleAgentPipeline()
