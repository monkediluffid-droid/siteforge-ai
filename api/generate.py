import json
import os
import re
import urllib.request
import urllib.error
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

            payload = {
                "input": f"{system_prompt}\n\nЗапрос пользователя: {prompt}",
                "response_format": {
                    "type": "json_object"
                }
            }

            url = f"[https://generativelanguage.googleapis.com/v1alpha/interactions?key=](https://generativelanguage.googleapis.com/v1alpha/interactions?key=){api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))

            text = ""
            if "outputs" in res_data and len(res_data["outputs"]) > 0:
                text = res_data["outputs"][-1].get("text", "")
            elif "output_text" in res_data:
                text = res_data["output_text"]

            text = text.strip()
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

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            self.send_json(500, {
                "error": f"API Error: {err_body}"
            })
        except Exception as e:
            self.send_json(500, {
                "error": str(e)
            })
