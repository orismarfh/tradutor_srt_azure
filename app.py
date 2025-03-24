from flask import Flask, request, render_template, send_file
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def translate_srt(text):
    prompt = (
        "This is an SRT subtitle file containing English text.\n"
        "Translate all spoken content into Japanese.\n"
        "Do not modify numbers or timestamps.\n"
        "Preserve the original SRT structure.\n\n"
        f"{text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional subtitle translator. Keep the structure intact."},
            {"role": "user", "content": prompt}
        ],
        timeout=120
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["srt_file"]
        if file:
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()

            if ext not in [".srt", ".txt"]:
                return "❌ Formato não suportado. Envie apenas arquivos .srt ou .txt", 400

            input_path = "uploaded" + ext
            output_path = "translated" + ext
            file.save(input_path)

            with open(input_path, "r", encoding="utf-8") as f:
                srt_text = f.read()

            translated = translate_srt(srt_text)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(translated)

            return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()


