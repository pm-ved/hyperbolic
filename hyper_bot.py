import asyncio
import logging

import httpx

from utils import convert_proxy_to_http, read_data_sheet

HYPERBOLIC_API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3-0324"
MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9
DELAY_BETWEEN_QUESTIONS = 45

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HyperpolicClient:
    def __init__(self, api_key: str, questions: list[str], proxy=None, **kwargs):
        self.api_key = api_key
        self.questions = questions
        self.client = httpx.AsyncClient(headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }, proxy=convert_proxy_to_http(proxy), timeout=30)

    async def get_response(self, question: str) -> str:
        data = {
            "messages": [{"role": "user", "content": question}],
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P
        }
        response = await self.client.post(HYPERBOLIC_API_URL, json=data)
        response.raise_for_status()
        json_response = response.json()
        return json_response.get("choices", [{}])[0].get("message", {}).get("content", "No answer")

    async def loop(self):
        for question in self.questions:
            try:
                response = await self.get_response(question)
                logger.info(f"Вопрос: {question}")
                logger.info(f"Ответ: {response}")
            except httpx.RequestError as e:
                logger.error(f"Ошибка при запросе к API: {e}")
            except Exception as e:
                logger.error(f"Неизвестная ошибка: {e}")
            finally:
                await asyncio.sleep(DELAY_BETWEEN_QUESTIONS)


def main():
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка чтения файла questions.txt: {e}")
        return

    if not questions:
        logger.error("В файле questions.txt нет вопросов.")
        return

    data = read_data_sheet("data.csv")
    tasks = []
    for row in data:
        client = HyperpolicClient(questions=questions, **row)
        tasks.append(asyncio.create_task(client.loop()))
    asyncio.gather(*tasks)


if __name__ == "__main__":
    main()
