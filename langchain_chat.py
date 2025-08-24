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
    """Handle conversation state, model selection, and token counting."""

    def __init__(self) -> None:
        self.config: Dict[str, str] = json.loads(CONFIG_PATH.read_text())
        self.models_map: Dict[str, List[str]] = self.config.get("models", {})
        self.provider: str = self.config.get("provider", "openai")
        default_model = self.models_map.get(self.provider)
        if isinstance(default_model, list):
            self.model = default_model[0]
        else:
            self.model = default_model
        self.llm = self._load_model(self.provider, self.model)
        self.history: List[Dict[str, str]] = self._load_history()
        self.token_counts: Dict[str, int] = {"read": 0, "created": 0, "cache": 0}
        self.available_models = [
            m
            for models in self.models_map.values()
            for m in (models if isinstance(models, list) else [models])
        ]

    def _load_model(self, provider: str, model_name: str):
        self.provider = provider
        self.model = model_name

        if provider == "openai":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=self.config.get("openai_api_key"),
            )
        if provider == "gemini" and ChatGoogleGenerativeAI is not None:
            return ChatGoogleGenerativeAI(
                google_api_key=self.config.get("gemini_api_key"),
                model=model_name,
            )
        if provider == "anthropic":
            return ChatAnthropic(
                model=model_name,
                anthropic_api_key=self.config.get("anthropic_api_key"),
            )
        raise ValueError(f"Unsupported provider: {provider}")

    def set_model(self, model_name: str) -> None:
        for provider, models in self.models_map.items():
            model_list = models if isinstance(models, list) else [models]
            if model_name in model_list:
                self.llm = self._load_model(provider, model_name)
                return
        raise ValueError(f"Unknown model: {model_name}")

    def _load_history(self) -> List[Dict[str, str]]:
        if HISTORY_PATH.exists():
            return json.loads(HISTORY_PATH.read_text())
        return []

    def _save_history(self) -> None:
        HISTORY_PATH.write_text(json.dumps(self.history, indent=2))

    def _count_tokens(self, text: str) -> int:
        return len(text.split())

    def _history_tokens(self) -> int:
        return sum(self._count_tokens(m["content"]) for m in self.history)

    def chat(self, user_input: str) -> str:
        cache_tokens = self._history_tokens()
        self.history.append({"role": "user", "content": user_input})
        read_tokens = self._count_tokens(user_input)
        messages = [
            HumanMessage(m["content"]) if m["role"] == "user" else AIMessage(m["content"])
            for m in self.history
        ]
        response = self.llm(messages)
        created_tokens = self._count_tokens(response.content)
        self.history.append({"role": "assistant", "content": response.content})
        self.token_counts = {
            "read": read_tokens,
            "created": created_tokens,
            "cache": cache_tokens,
        }
        self._save_history()
        return response.content

    def reset_history(self) -> None:
        self.history = []
        self.token_counts = {"read": 0, "created": 0, "cache": 0}
        self._save_history()
