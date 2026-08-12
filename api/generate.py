import json
import os
from http.server import BaseHTTPRequestHandler
from google import genai
from google.genai import types


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

            client = genai.Client(api_key=api_key)

            system_prompt = """
Ты — SiteForge AI, профессиональный AI-конструктор сайтов.

Пользователь описывает сайт обычными словами.

Твоя задача — создать готовый современный сайт.

Верни ТОЛЬКО JSON следующего формата:

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
- JavaScript для интерактивности;
- HTML должен быть готов к запуску;
- CSS должен быть полноценным;
- JavaScript должен быть полноценным.

Не используй Markdown.
Не добавляй ```html.
Не добавляй ```css.
Не добавляй ```javascript.

Верни только JSON.
"""

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )

            text = response.text.strip()

            try:
                result = json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}")

                if start != -1 and end != -1:
                    result = json.loads(text[start:end + 1])
                else:
                    raise ValueError("AI вернул неправильный JSON")

            self.send_json(200, result)

        except Exception as e:
            self.send_json(500, {
                "error": str(e)
            })
