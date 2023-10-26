from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse
from server.utils import BOTS, Bot
from uuid import uuid4
import base64
import json

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        match (parsed.path):
            case "/api/register":
                id = str(uuid4())
                BOTS[id] = Bot()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"id": id}).encode("utf-8"))
            case _:
                super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        match (parsed.path):
            case "/api/stt":
                data = self.rfile.read(int(self.headers['Content-Length'])).decode("utf-8")
                data = json.loads(data)
                audio_data: str = data["audio"]
                if not audio_data.startswith("data:audio/wav;"):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid audio data"}).encode("utf-8"))
                    return
                audio_data = audio_data.split(',')[1]
                audio_data = base64.b64decode(audio_data)
                text = BOTS[data["id"]].speech_to_text(audio_data)
                response = {"text": text}
                response_text = json.dumps(response)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", f"{len(response_text)}")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response_text.encode("utf-8"))
            case "/api/chat":
                data = self.rfile.read(int(self.headers['Content-Length'])).decode("utf-8")
                data = json.loads(data)
                message = data["message"]
                text = BOTS[data["id"]].chat(message)
                response = {"response": text}
                response_text = json.dumps(response)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", f"{len(response_text)}")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response_text.encode("utf-8"))
            case _:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404")