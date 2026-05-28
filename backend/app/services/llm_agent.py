import json
from openai import OpenAI
from app.core.config import settings

class MultiAgentPipeline:
    def __init__(self):
        # Configure client to support both standard OpenAI and compatible endpoints
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
        }
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
            
        # Explicitly use a fresh client to avoid potential proxy argument conflicts in some environments
        self.client = OpenAI(**client_kwargs)
        # We can change the model name via env or keep a default suitable for Siliconflow/OpenAI
        self.model = "gpt-4o-mini" if not settings.OPENAI_BASE_URL else "deepseek-ai/DeepSeek-V4-Flash"

    def _call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "timeout": 30.0, # Add 30s timeout
        }
        
        try:
            print(f"  [LLM] Calling {self.model}...")
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [LLM] Error: {e}")
            if "Timeout" in str(e) or "timed out" in str(e):
                return "{}" if json_mode else ""
            raise e

    def router_agent(self, text: str) -> dict:
        """
        Determines if the text is relevant and categorizes it.
        """
        system_prompt = """
        你是一个专门为【日本私费外国留学生（学部考学）】筛选升学情报的专家。
        阅读用户提供的日文新闻文本，判断其是否对外国留学生有价值。
        
        【必须接收】的条件（满足其一即可）：
        1. 明确提及「私費外国人留学生」、「留学生入試」、「EJU」相关的出愿情报、变更或通知。
        2. 属于面向所有考生的「Open Campus (オープンキャンパス)」、「进学说明会/相谈会 (進学説明会/相談会)」、「体验讲座」等公开活动。

        【必须拒绝】的条件（判断为“无关”）：
        1. 仅限日本国内高中生的常规考试（如：一般選抜、共通テスト、学校推薦型選抜、総合型選抜，且未明确表明留学生可用）。
        2. 与学部升学完全无关的日常新闻（如：教授获奖、放假通知、在校生社团活动、大学院/研究生院入试）。
        
        请严格以JSON格式输出，不要包含任何其他文字或Markdown标记，格式如下：
        {
            "is_relevant": true/false,
            "category": "出愿情报" | "Open Campus" | "讲座" | "变更" | "其他" | "无关"
        }
        """
        
        result_str = self._call_llm(system_prompt, text)
        try:
            # Clean up markdown if model outputs it
            if result_str.startswith("```json"):
                result_str = result_str.replace("```json\n", "").replace("```", "")
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"is_relevant": False, "category": "解析失败"}

    def extractor_agent(self, text: str) -> str:
        """
        Extracts key facts and dates from relevant text.
        """
        system_prompt = """
        你是一个情报提取专家。请从以下日文大学通知中提取出关键的“时间节点（Event Dates, Deadlines）”和“具体事项/前因后果”。
        要求：
        1. 保持时间信息的准确性。
        2. 用简洁的列表形式呈现提取出的事实。
        3. 尽量使用中文进行记录。
        """
        return self._call_llm(system_prompt, text)

    def summarizer_agent(self, extracted_facts: str) -> str:
        """
        Creates a strict 100-word summary from extracted facts.
        """
        system_prompt = """
        你是一个精炼的新闻编辑。基于用户提供的提取信息，撰写一段高度概括的中文摘要。
        要求：
        1. 语感专业、客观。
        2. 字数严格限制在100字左右。
        3. 必须包含最重要的时间节点和核心事件。
        """
        return self._call_llm(system_prompt, extracted_facts)

    def process_news(self, raw_text: str) -> dict:
        """
        The main pipeline integrating all agents.
        """
        # Step 1: Route
        route_decision = self.router_agent(raw_text)
        if not route_decision.get("is_relevant"):
            return None
            
        # Step 2: Extract
        extracted_facts = self.extractor_agent(raw_text)
        
        # Step 3: Summarize
        summary = self.summarizer_agent(extracted_facts)
        
        # Final formatting
        return {
            "category": route_decision.get("category", "其他"),
            "summary": summary,
            "important_dates": extracted_facts
        }

llm_pipeline = MultiAgentPipeline()
