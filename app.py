from flask import Flask, render_template, request, redirect, url_for
from langchain_chat import ChatHandler

app = Flask(__name__)
chat_handler = ChatHandler()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_message = request.form.get("message", "")
        if user_message:
            chat_handler.chat(user_message)
        return redirect(url_for("index"))
    return render_template("index.html", history=chat_handler.history, provider=chat_handler.provider)


@app.route("/reset")
def reset():
    chat_handler.reset_history()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
