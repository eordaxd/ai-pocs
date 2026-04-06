"""
Experiment: MasterDP Chatbot
A web chatbot that answers questions about the Master en Dirección de Proyectos (UVa).
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import anthropic

from knowledge_base import MASTER_DP_KNOWLEDGE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

app = Flask(__name__)


def get_client():
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = f"""Eres un asistente virtual especializado en el Máster Oficial en Dirección de Proyectos de la Universidad de Valladolid. Tu objetivo es ayudar a los usuarios respondiendo preguntas sobre el programa, la admisión, el profesorado, las asignaturas, los plazos de matrícula y cualquier otro aspecto del máster.

Reglas:
- Responde siempre en español, de forma clara y amable.
- Basa tus respuestas ÚNICAMENTE en la información proporcionada a continuación. No inventes datos.
- Si no tienes la información para responder una pregunta, indica que no dispones de esa información y sugiere contactar directamente con el máster (master.direccion.proyectos@uva.es o teléfono 983 18 58 33).
- Cuando sea relevante, incluye enlaces a la web oficial: https://www.masterdp.uva.es/
- Sé conciso pero completo en tus respuestas.
- Usa formato con viñetas o listas cuando ayude a la claridad.

Información del Máster:
{MASTER_DP_KNOWLEDGE}
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    history = data.get("history", [])

    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    assistant_text = response.content[0].text
    return jsonify({"response": assistant_text})


if __name__ == "__main__":
    app.run(debug=True, port=5002)
