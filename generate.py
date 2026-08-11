import json
import os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "html": {"type": "string"},
        "css": {"type": "string"},
        "js": {"type": "string"}
    },
    "required": ["name", "description", "html", "css", "js"],
    "additionalProperties": False
}

SYSTEM = """You are SiteForge AI, a professional website generator.
Turn the user's idea into a polished responsive single-page website.
Return only the structured object requested by the schema.
Generate real standalone HTML body markup, CSS and vanilla JavaScript.
Use semantic accessible HTML, modern animations, responsive design and
a premium visual style. Do not use markdown fences, external JS libraries,
API keys, secrets, server code or credentials in the generated frontend.
Use CSS shapes/gradients when images are unavailable."""

def generate(prompt):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured in Vercel")
    client = OpenAI(api_key=key)
    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-5"),
        instructions=SYSTEM,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "site_project",
                "strict": True,
                "schema": SCHEMA
            }
        }
    )
    return json.loads(response.output_text)

class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            prompt = str(body.get("prompt", "")).strip()
            if len(prompt) < 3:
                return self._send(400, {"error": "Напиши идею сайта"})
            if len(prompt) > 8000:
                return self._send(400, {"error": "Запрос слишком длинный"})
            site = generate(prompt)
            self._send(200, {"site": site})
        except Exception as e:
            self._send(500, {"error": str(e)})
