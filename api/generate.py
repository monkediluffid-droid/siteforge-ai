import json
import os
import re
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

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )

            text = response.text.strip()

            text = re.sub(r"^
http://googleusercontent.com/immersive_entry_chip/0

---

### Шаг 3. Проверьте переменную окружения в Vercel

Перейдите в настройки Vercel: **Project Settings** -> **Environment Variables**.
1. Убедитесь, что переменная называется строго **`GEMINI_API_KEY`**.
2. В поле **Value** вставьте заново ваш API ключ от Google AI Studio (он начинается на `AIzaSy...`). Убедитесь, что нет пробелов по краям.
3. Сохраните переменную.

После этого сохраните изменения в GitHub (**Commit**) и дождитесь статуса **Ready** в Vercel.
