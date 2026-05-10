from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os, base64, tempfile
import PyPDF2
from docx import Document
import openpyxl

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")
SYSTEM_PROMPT = """Tu es Zina IA, un assistant professionnel et formel.
Tu réponds toujours de manière claire, précise et structurée.
Tu utilises le français par défaut."""

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
        parts = [SYSTEM_PROMPT]
        
        if file_data and file_type:
            if file_type.startswith("image/"):
                parts.append({"mime_type": file_type, "data": file_data})
            elif file_type == "application/pdf":
                pdf_bytes = base64.b64decode(file_data)
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    f.write(pdf_bytes)
                    tmp_path = f.name
                reader = PyPDF2.PdfReader(tmp_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                parts.append(f"Contenu du PDF:\n{text}")
            elif "word" in file_type or "document" in file_type:
                docx_bytes = base64.b64decode(file_data)
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                    f.write(docx_bytes)
                    tmp_path = f.name
                doc = Document(tmp_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                parts.append(f"Contenu du document:\n{text}")
            elif "excel" in file_type or "spreadsheet" in file_type:
                xlsx_bytes = base64.b64decode(file_data)
                with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
                    f.write(xlsx_bytes)
                    tmp_path = f.name
                wb = openpyxl.load_workbook(tmp_path)
                text = ""
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    for row in ws.iter_rows(values_only=True):
                        text += " | ".join([str(c) for c in row if c]) + "\n"
                parts.append(f"Contenu Excel:\n{text}")
        
        if messages:
            parts.append(messages[-1]["content"])
        
        response = model.generate_content(parts)
        return jsonify({"reply": response.text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ Zina IA démarrée sur http://localhost:5000")
    app.run(debug=True, port=5000)