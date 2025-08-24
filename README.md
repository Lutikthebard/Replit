# LangChain Chat Demo

This project provides a minimal Flask web interface backed by [LangChain](https://python.langchain.com/) that allows chatting with different large language models. The provider and API keys are configured in `config.json` and include OpenAI, Google Gemini, and Anthropic.

## Features

- Switch between OpenAI, Gemini, or Anthropic models via `config.json`.
- Conversation history stored in `history.json` with ability to reset.
- Simple responsive user interface built with Flask templates.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Edit `config.json` with your API keys and desired provider.

3. Run the application:

```bash
python app.py
```

Then open `http://localhost:5000` in your browser to start chatting.

## Resetting Conversation

Use the **Reset** link on the page to clear stored chat history.
