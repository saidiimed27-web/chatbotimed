from flask import Flask, render_template, request, jsonify
from groq import Groq
import json
import os
from datetime import datetime

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SYSTEM_PROMPT = """Tu es un assistant IA serviable et amical.
Tu réponds toujours en français sauf si l'utilisateur écrit dans une autre langue.
Tes réponses sont claires, concises et bien structurées."""

HISTORIQUE_FILE = "historique.json"

def sauvegarder(messages):
    historique = []
    if os.path.exists(HISTORIQUE_FILE):
        with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
            historique = json.load(f)
    historique.append({
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "messages": messages
    })
    with open(HISTORIQUE_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "Aucun message fourni"}), 400
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=1024,
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        sauvegarder(messages)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ Chatbot démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)