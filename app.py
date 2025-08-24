from flask import Flask, render_template, request, redirect, url_for
from langchain_chat import ChatHandler
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
chat_handler = ChatHandler()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_message = request.form.get("message", "")
        if user_message:
            chat_handler.chat(user_message)
        return redirect(url_for("index"))
    return render_template(
        "index.html",
        history=chat_handler.history,
        provider=chat_handler.provider,
        models=chat_handler.available_models(),
        model_provider=chat_handler.model_provider,
        current_model=chat_handler.current_model,
        tokens=chat_handler.token_usage,
        expert_mode=chat_handler.use_expert_mode,
        system_prompt=chat_handler.last_system_prompt,
        system_prompt_template=chat_handler.system_prompt_template,
    )


@app.route("/reset")
def reset():
    chat_handler.reset_history()
    return redirect(url_for("index"))


@app.route("/set_model", methods=["POST"])
def set_model():
    model = request.form.get("model")
    if model:
        chat_handler.set_model(model)
    return redirect(url_for("index"))


@app.route("/toggle_mode", methods=["POST"])
def toggle_mode():
    chat_handler.use_expert_mode = "true" in request.form.getlist("expert_mode")
    return redirect(url_for("index"))


@app.route("/set_prompt", methods=["POST"])
def set_prompt():
    prompt = request.form.get("prompt_template")
    if prompt is not None:
        chat_handler.set_system_prompt_template(prompt)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
