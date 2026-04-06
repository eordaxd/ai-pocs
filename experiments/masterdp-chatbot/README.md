# Experiment: MasterDP Chatbot

## What

A web chatbot that answers questions about the Master en Dirección de Proyectos de la Universidad de Valladolid, using content scraped from https://www.masterdp.uva.es/.

## Why

Provide an easy, conversational way to get information about the program (curriculum, admission, deadlines, faculty, etc.) without navigating the full website.

## How to Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
python main.py
```

Then open http://localhost:5002 in your browser.

## Results / Findings

<!-- What did you learn? Even "didn't work because X" is valuable. -->
