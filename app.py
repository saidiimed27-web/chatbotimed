from flask import Flask, render_template, request, jsonify
from groq import Groq
import google.generativeai as genai
import os, base64, tempfile

app = Flask(__name__)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")

SYSTEM_PROMPT = """Tu es Zina IA, une assistante professionnelle et formelle.
Tu réponds toujours de manière claire, précise et structurée en français."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    file_data = data.get("file", None)
    file_type = data.get("file_type", None)

    try:
        if file_data and file_type and file_type.startswith("image/"):
            parts = [SYSTEM_PROMPT]
            parts.append({"mime_type": file_type, "data": file_data})
            if messages:
                parts.append(messages[-1]["content"])
            response = gemini_model.generate_content(parts)
            return jsonify({"reply": response.text})

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=1024,
        )
        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ Zina IA démarrée sur http://localhost:5000")
    app.run(debug=True, port=5000)