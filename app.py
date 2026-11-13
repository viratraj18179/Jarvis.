
import os
from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

api_key = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=api_key) if api_key else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"error": "API key not configured"}), 503

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message"}), 400

    if len(message) > 5000:
        return jsonify({"error": "Message too long"}), 400

    try:
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
            max_tokens=1000,
            system="You are JARVIS, a helpful, intelligent and polite personal AI assistant.",
            messages=[
                {"role": "user", "content": message}
            ]
        )

        answer = "".join(
            block.text for block in response.content
            if block.type == "text"
        )

        return jsonify({"reply": answer})

    except Exception:
        app.logger.exception("Claude API error")
        return jsonify({"error": "AI service unavailable"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
