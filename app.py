from flask import Flask, render_template, request, jsonify
from groq import Groq
import os, base64

app = Flask(__name__)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
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
        groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if file_data and file_type:
            last_text = messages[-1]["content"] if messages else "Analyse cette image"
            groq_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": last_text},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{file_type};base64,{file_data}"
                    }}
                ]
            })
        else:
            groq_messages += messages

        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=groq_messages,
            max_tokens=1024,
        )
        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ Zina IA démarrée sur http://localhost:5000")
    app.run(debug=True, port=5000)