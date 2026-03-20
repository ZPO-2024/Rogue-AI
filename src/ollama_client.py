"""
ROGUE — Ollama Local LLM Client
"""
import json, logging, requests
from typing import Optional
from .config import config

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.host = config.OLLAMA_HOST
        self.default_model = config.OLLAMA_DEFAULT_MODEL
        self.vision_model = config.OLLAMA_VISION_MODEL
        self.chat_model = config.OLLAMA_CHAT_MODEL
        self.timeout = config.OLLAMA_TIMEOUT

    def health_check(self) -> dict:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"status": "ok", "host": self.host, "models": models}
        except Exception as e:
            return {"status": "error", "error": str(e), "host": self.host}

    def generate(self, prompt: str, model: Optional[str] = None,
                 system: Optional[str] = None, stream: bool = False,
                 images: Optional[list] = None) -> str:
        model = model or self.default_model
        payload = {"model": model, "prompt": prompt, "stream": stream}
        if system: payload["system"] = system
        if images: payload["images"] = images
        try:
            resp = requests.post(f"{self.host}/api/generate", json=payload,
                                 timeout=self.timeout, stream=stream)
            resp.raise_for_status()
            if stream: return self._collect_stream(resp)
            return resp.json().get("response", "").strip()
        except requests.exceptions.ConnectionError:
            return "[ROGUE: Ollama offline — run: ollama serve]"
        except Exception as e:
            return f"[ROGUE error: {e}]"

    def _collect_stream(self, resp) -> str:
        parts = []
        for line in resp.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    parts.append(chunk.get("response", ""))
                    if chunk.get("done"): break
                except json.JSONDecodeError: continue
        return "".join(parts).strip()

    def chat(self, messages: list, model: Optional[str] = None, stream: bool = False) -> str:
        model = model or self.chat_model
        payload = {"model": model, "messages": messages, "stream": stream}
        try:
            resp = requests.post(f"{self.host}/api/chat", json=payload,
                                 timeout=self.timeout, stream=stream)
            resp.raise_for_status()
            if stream:
                parts = []
                for line in resp.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            parts.append(chunk.get("message", {}).get("content", ""))
                            if chunk.get("done"): break
                        except json.JSONDecodeError: continue
                return "".join(parts).strip()
            return resp.json().get("message", {}).get("content", "").strip()
        except Exception as e:
            return f"[ROGUE chat error: {e}]"

    def vision(self, prompt: str, image_b64: str) -> str:
        return self.generate(prompt=prompt, model=self.vision_model, images=[image_b64])

ollama = OllamaClient()
