import json
from pathlib import Path
from typing import List, Dict

from langchain.schema import HumanMessage, AIMessage
try:
    from langchain_openai import ChatOpenAI
except ImportError:  # fallback for older langchain versions
    from langchain.chat_models import ChatOpenAI  # type: ignore
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None  # type: ignore
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    from langchain.chat_models import ChatAnthropic  # type: ignore

CONFIG_PATH = Path("config.json")
HISTORY_PATH = Path("history.json")


class ChatHandler:
    """Handle conversation state and model selection."""

    def __init__(self) -> None:
        self.config: Dict[str, str] = json.loads(CONFIG_PATH.read_text())
        self.provider: str = self.config.get("provider", "openai")
        self.llm = self._load_model()
        self.history: List[Dict[str, str]] = self._load_history()

    def _load_model(self):
        if self.provider == "openai":
            return ChatOpenAI(openai_api_key=self.config.get("openai_api_key"))
        if self.provider == "gemini" and ChatGoogleGenerativeAI is not None:
            return ChatGoogleGenerativeAI(
                google_api_key=self.config.get("gemini_api_key"),
                model="gemini-pro",
            )
        if self.provider == "anthropic":
            return ChatAnthropic(
                anthropic_api_key=self.config.get("anthropic_api_key"),
            )
        raise ValueError(f"Unsupported provider: {self.provider}")

    def _load_history(self) -> List[Dict[str, str]]:
        if HISTORY_PATH.exists():
            return json.loads(HISTORY_PATH.read_text())
        return []

    def _save_history(self) -> None:
        HISTORY_PATH.write_text(json.dumps(self.history, indent=2))

    def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        messages = [
            HumanMessage(m["content"]) if m["role"] == "user" else AIMessage(m["content"])
            for m in self.history
        ]
        response = self.llm(messages)
        self.history.append({"role": "assistant", "content": response.content})
        self._save_history()
        return response.content

    def reset_history(self) -> None:
        self.history = []
        self._save_history()
