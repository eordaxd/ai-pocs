import sys
import os

# Path setup — must happen before local imports
_src_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_src_dir)                        # pocs/qa-chatbot/
_shared_dir = os.path.normpath(os.path.join(_src_dir, "../../../shared"))  # ai-pocs/shared/
for _p in [_root_dir, _shared_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.indexer import Indexer
from src.chatbot import QAChatbot
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.compressed import CompressedRetriever
from clients.claude_client import ClaudeClient

console = Console()

BASE_DIR = Path(_root_dir)
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"

STRATEGIES = ["semantic", "keyword", "hybrid", "compressed"]


def cmd_index(args):
    console.print(f"\n[bold]Indexing documents from [cyan]{DOCS_DIR}[/cyan][/bold]")
    indexer = Indexer(DATA_DIR)
    try:
        indexer.build(DOCS_DIR)
        console.print(f"[green]Index saved to {DATA_DIR}[/green]\n")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


def cmd_chat(args):
    strategy = args.strategy
    indexer = Indexer(DATA_DIR)
    try:
        semantic, keyword = indexer.load()
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    claude = ClaudeClient(max_tokens=2048)

    if strategy == "semantic":
        retriever = semantic
    elif strategy == "keyword":
        retriever = keyword
    elif strategy == "hybrid":
        retriever = HybridRetriever(semantic, keyword)
    elif strategy == "compressed":
        retriever = CompressedRetriever(semantic, ClaudeClient(max_tokens=512))
    else:
        console.print(f"[red]Unknown strategy: {strategy}[/red]")
        sys.exit(1)

    chatbot = QAChatbot(retriever, claude, top_k=args.top_k)

    console.print(Panel(
        f"[bold]Document Q&A Chatbot[/bold]\n"
        f"Strategy: [cyan]{strategy}[/cyan] | Top-k: [cyan]{args.top_k}[/cyan]\n"
        f"Type [yellow]exit[/yellow] to quit | [yellow]clear[/yellow] to reset history",
        title="Q&A",
        border_style="blue",
    ))

    while True:
        try:
            question = Prompt.ask("\n[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if question.strip().lower() in ("exit", "quit"):
            console.print("[yellow]Goodbye![/yellow]")
            break

        if question.strip().lower() == "clear":
            chatbot.clear_history()
            console.print("[yellow]Conversation history cleared.[/yellow]")
            continue

        if not question.strip():
            continue

        with console.status("[bold blue]Thinking...[/bold blue]"):
            answer, sources = chatbot.ask(question)

        console.print(f"\n[bold blue]Assistant:[/bold blue] {answer}")
        if sources:
            console.print(f"\n[dim]Sources: {', '.join(sources)}[/dim]")


def cmd_status(args):
    indexer = Indexer(DATA_DIR)
    info = indexer.status()

    if not info["indexed"]:
        console.print("[yellow]No index found. Run `python src/main.py index` first.[/yellow]")
        return

    table = Table(title="Index Status", show_header=True)
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Total chunks", str(info["chunks"]))
    table.add_row("Indexed documents", str(len(info["sources"])))
    for src in info["sources"]:
        table.add_row("", f"  • {src}")

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Q&A Chatbot — ask questions about your documents"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="Index all documents in the docs/ folder")

    chat_p = sub.add_parser("chat", help="Start an interactive Q&A session")
    chat_p.add_argument(
        "--strategy",
        choices=STRATEGIES,
        default="hybrid",
        help="Retrieval strategy (default: hybrid)",
    )
    chat_p.add_argument(
        "--top-k",
        type=int,
        default=5,
        dest="top_k",
        help="Number of chunks to retrieve per query (default: 5)",
    )

    sub.add_parser("status", help="Show what is currently indexed")

    args = parser.parse_args()

    if args.command == "index":
        cmd_index(args)
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "status":
        cmd_status(args)


if __name__ == "__main__":
    main()
