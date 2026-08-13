import json
import os
import re
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
            # Безопасный импорт google-genai
            from google import genai
            from google.genai import types

            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)

            data = json.loads(raw.decode("utf-8") or "{}")
            prompt = data.get("prompt", "").strip()

            if not prompt:
                self.send_json(400, {"error": "Напишите описание сайта"})
                return

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.send_json(500, {"error": "GEMINI_API_KEY не настроен в Vercel"})
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
- анимации, hover-эффекты;
- кнопки, карточки, хорошая типографика;
- JavaScript для интерактивности.

ОБЯЗАТЕЛЬНО возвращай все 4 ключа: title, html, css, js.
"""

            # Используем актуальную модель Gemini 2.5 Flash
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

#### 3. Проверьте переменную окружения в Vercel
1. Откройте **Vercel Dashboard** -> ваш проект -> **Settings** -> **Environment Variables**.
2. Проверьте, чтобы имя переменной было строго `GEMINI_API_KEY`.
3. Убедитесь, что ваш API-ключ скопирован без лишних символов и кавычек.
4. Нажмите **Redeploy** в панели Vercel (в вкладке *Deployments* -> *...* -> *Redeploy*), чтобы новые зависимости и код заступили в силу.
