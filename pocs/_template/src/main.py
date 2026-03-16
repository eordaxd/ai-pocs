"""
PoC: <name>
"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def main():
    # TODO: implement your PoC here
    pass


if __name__ == "__main__":
    main()
