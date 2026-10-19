"""hello-openrouter: ask a Claude model and a Mistral model the same question
and show both answers side by side, with response time and tokens used.

Run it with:  uv run hello-openrouter "your question"
"""

import argparse
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import openai
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from hello_openrouter.config import DEFAULT_QUESTION, MODELS, OPENROUTER_BASE_URL

console = Console()


@dataclass
class ModelResult:
    """What we get back from one model: either an answer or an error message."""

    model: str
    answer: str = ""
    seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None


def get_api_key() -> str:
    """Read the OpenRouter key from .env. Stop with a clear message if it's missing."""
    load_dotenv()
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        console.print(
            "[bold red]Missing API key.[/] Add a line OPENROUTER_API_KEY=... to the .env file "
            "in the project folder. Get a key at https://openrouter.ai/keys"
        )
        sys.exit(1)
    return key


def ask_model(client: openai.OpenAI, model: str, question: str) -> ModelResult:
    """Send the question to one model and measure how long the answer takes."""
    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
        )
    # Turn the SDK's technical errors into messages a person can act on.
    except openai.AuthenticationError:
        return ModelResult(model, error="Your API key was rejected. Check OPENROUTER_API_KEY in .env.")
    except (openai.NotFoundError, openai.BadRequestError) as e:
        return ModelResult(
            model,
            error=f"Model '{model}' is not available on OpenRouter (status {e.status_code}). "
            "Check the ID in config.py against https://openrouter.ai/models",
        )
    except openai.RateLimitError:
        return ModelResult(model, error="Rate limit reached or out of credits. Wait a moment, or check your OpenRouter balance.")
    except openai.APIConnectionError:
        return ModelResult(model, error="Could not reach OpenRouter. Check your internet connection.")
    except openai.APIStatusError as e:
        return ModelResult(model, error=f"OpenRouter returned an error (status {e.status_code}): {e.message}")
    seconds = time.perf_counter() - start

    # Some providers can return an empty answer or no usage data, so we guard against None.
    answer = response.choices[0].message.content or "(empty answer)"
    usage = response.usage
    return ModelResult(
        model=model,
        answer=answer,
        seconds=seconds,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
    )


def show_results(question: str, results: list) -> None:
    """Print the answers in a side-by-side table, with time and tokens at the bottom."""
    table = Table(title=f"Question: {question}", show_lines=True, expand=True)
    for result in results:
        table.add_column(result.model, ratio=1)

    answers = [f"[red]{r.error}[/]" if r.error else r.answer for r in results]
    stats = [
        "-" if r.error else (
            f"Time: {r.seconds:.2f} s\n"
            f"Tokens: {r.input_tokens} in / {r.output_tokens} out / {r.input_tokens + r.output_tokens} total"
        )
        for r in results
    ]
    table.add_row(*answers)
    table.add_row(*stats)
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare a Claude model and a Mistral model on the same question.")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION, help="The question to ask (in quotes).")
    args = parser.parse_args()

    client = openai.OpenAI(base_url=OPENROUTER_BASE_URL, api_key=get_api_key())

    # One model after the other: simpler, and the timings don't affect each other.
    results = []
    for model in MODELS:
        with console.status(f"Asking {model}..."):
            results.append(ask_model(client, model, args.question))

    show_results(args.question, results)


if __name__ == "__main__":
    main()
