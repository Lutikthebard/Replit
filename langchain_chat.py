import json
from pathlib import Path
from typing import List, Dict, Tuple

from langchain.schema import HumanMessage, AIMessage
from langchain_community.callbacks.manager import get_openai_callback
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
        self.models: Dict[str, str] = self.config.get("models", {})
        self.model_provider: Dict[str, str] = {
            model: prov for prov, model in self.models.items()
        }
        self.provider: str = self.config.get("provider", "openai")
        self.current_model: str = self.models.get(self.provider, "")
        self.llm = self._load_model()
        self.history: List[Dict[str, str]] = self._load_history()
        self.token_usage: Dict[str, int] = {"read": 0, "created": 0, "cache": 0}

    def _load_model(self):
        model_name = self.current_model
        if not model_name:
            raise ValueError(f"Model not specified for provider: {self.provider}")

        if self.provider == "openai":
            return ChatOpenAI(
                model=model_name,
                openai_api_key=self.config.get("openai_api_key"),
            )
        if self.provider == "gemini" and ChatGoogleGenerativeAI is not None:
            return ChatGoogleGenerativeAI(
                google_api_key=self.config.get("gemini_api_key"),
                model=model_name,
            )
        if self.provider == "anthropic":
            return ChatAnthropic(
                model=model_name,
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
        if self.provider == "openai":
            with get_openai_callback() as cb:
                response = self.llm.invoke(messages)
            read, created, cache = cb.prompt_tokens, cb.completion_tokens, cb.prompt_tokens_cached
        else:
            response = self.llm.invoke(messages)
            read, created, cache = self._extract_usage(response)
        self.token_usage["read"] += read
        self.token_usage["created"] += created
        self.token_usage["cache"] += cache
        self.history.append({"role": "assistant", "content": response.content})
        self._save_history()
        return response.content

    def _extract_usage(self, response) -> Tuple[int, int, int]:
        metadata = getattr(response, "response_metadata", {})
        usage = metadata.get("token_usage", {})
        read = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
        created = usage.get("completion_tokens") or usage.get("output_tokens") or 0
        cache = (
            usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
            if isinstance(usage.get("prompt_tokens_details"), dict)
            else usage.get("cached_tokens", 0)
        )
        return read, created, cache

    def available_models(self) -> List[str]:
        return list(self.model_provider.keys())

    def set_model(self, model_name: str) -> None:
        provider = self.model_provider.get(model_name)
        if not provider:
            raise ValueError(f"Unknown model: {model_name}")
        self.provider = provider
        self.current_model = model_name
        self.llm = self._load_model()

    def reset_history(self) -> None:
        self.history = []
        self.token_usage = {"read": 0, "created": 0, "cache": 0}
        self._save_history()
