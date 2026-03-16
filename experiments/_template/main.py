"""
Experiment: <name>
"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def main():
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, Claude!"}
        ],
    )
    print(message.content[0].text)


if __name__ == "__main__":
    main()
