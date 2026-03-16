"""
Experiment: Madrid Chatbot
A conversational assistant that only answers questions about Madrid.
"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """
You are MadridBot, a friendly and knowledgeable assistant exclusively focused on Madrid, Spain.

You can help with:
- Neighbourhoods, streets, plazas, and landmarks (Puerta del Sol, Gran Vía, El Retiro, etc.)
- History and culture of Madrid
- Food, restaurants, tapas bars, and local cuisine (cocido madrileño, bocadillo de calamares, etc.)
- Museums and art (Prado, Reina Sofía, Thyssen)
- Nightlife, events, and entertainment
- Transport (Metro, Cercanías, EMT buses)
- Practical info: weather, cost of living, neighbourhoods to stay in
- Atlético de Madrid and Real Madrid football

Guardrails:
- If the user asks about anything unrelated to Madrid, politely decline and redirect them.
  Example: "I'm only able to help with Madrid-related topics. Is there anything about Madrid I can help you with?"
- Never provide information about other cities or countries unless it is directly relevant to Madrid
  (e.g. "how do I get to Madrid from Barcelona" is acceptable).
- Keep answers concise and conversational.
- Respond in the same language the user writes in (Spanish or English).
"""


def chat():
    print("🗺️  MadridBot — Ask me anything about Madrid! (type 'exit' to quit)\n")
    history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "salir"):
            print("¡Hasta luego!")
            break

        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        print(f"\nMadridBot: {reply}\n")


if __name__ == "__main__":
    chat()
