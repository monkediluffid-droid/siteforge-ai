import json
import os
import re
import requests
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)

            data = json.loads(raw.decode("utf-8"))
            prompt = data.get("prompt", "").strip()

            if not prompt:
                self.send_json(400, {
                    "error": "Напиши описание сайта"
                })
                return

            api_key = os.environ.get("GEMINI_API_KEY")

            if not api_key:
                self.send_json(500, {
                    "error": "GEMINI_API_KEY не настроен в Vercel"
                })
                return

            system_prompt = """
Ты — SiteForge AI, профессиональный AI-конструктор сайтов.

Пользователь описывает сайт обычными словами.

Твоя задача — создать готовый современный сайт.

Верни ТОЛЬКО валидный JSON следующего формата:

{
  "title": "Название сайта",
  "html": "полный HTML",
  "css": "полный CSS",
  "js": "полный JavaScript"
}

Требования:
- современный дизайн;
- адаптивность для телефона и компьютера;
- красивые градиенты;
- анимации;
- hover-эффекты;
- кнопки;
- карточки;
- хорошая типографика;
- полноценные секции;
- JavaScript для интерактивности.

ОБЯЗАТЕЛЬНО возвращай все 4 ключа: title, html, css, js.
Не используй разметку Markdown (никаких ```json).
"""

         url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\nЗапрос пользователя: {prompt}"
                    }]
                }],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }

            resp = requests.post(url, json=payload, timeout=60)
            res_data = resp.json()

            if resp.status_code != 200:
                error_msg = res_data.get("error", {}).get("message", "API Error")
                self.send_json(500, {"error": f"Gemini API: {error_msg}"})
                return

            text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()

            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    result = json.loads(text[start:end + 1])
                else:
                    raise ValueError("AI вернул некорректный ответ")

            response_data = {
                "title": result.get("title", "Мой сайт"),
                "html": result.get("html", ""),
                "css": result.get("css", ""),
                "js": result.get("js", "")
            }

            self.send_json(200, response_data)

        except Exception as e:
            self.send_json(500, {
                "error": str(e)
            })
