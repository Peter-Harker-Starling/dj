from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai
from django.conf import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY) # 從 settings 去讀 GEMINI_API_KEY

def ai_parse(user_input):
    today = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d")
    CATEGORIES = ["餐飲", "交通", "娛樂", "生活", "其他"]

    prompt = f"""
    你是記帳解析器。將輸入轉為 JSON 陣列。
    分類只能選：{", ".join(CATEGORIES)}。
    格式範例：[{{"amount": 100, "item": "項目", "category": "分類"}}]
    
    輸入："{user_input}"
    """

    response = client.models.generate_content(
        model="models/gemma-3-27b-it",
        contents=prompt
    )

    output = response.text.strip().replace("```json", "").replace("```", "")

    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
    except json.JSONDecodeError:
        data = [{"amount": None, "item": user_input, "category": "其他"}]

    for item in data:
        item["date"] = today

    return data