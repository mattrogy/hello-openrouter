# hello-openrouter

A small command-line tool that asks **two AI models the same question**, one from Anthropic (Claude)
and one from Mistral, and shows their answers **side by side**, with **response time** and **tokens used**
for each.

## Why this matters for enterprise AI deployment

When a company rolls out an AI assistant, "which model?" is one of the first decisions, and it is rarely
obvious. Models differ on:

- **Answer quality and style**: one may be more thorough, another more concise or more on-brand.
- **Speed**: a customer-facing chatbot needs fast replies; an overnight report does not.
- **Cost**: providers bill per token (roughly, per word piece), so token counts translate directly into money at scale.
- **Sovereignty and compliance**: a European company may prefer a European provider such as Mistral for data-residency reasons.

The sensible way to decide is to run the client's real questions through several candidate models and
compare the results. This tool is the smallest version of that process. It uses **OpenRouter**, a single
gateway to many AI providers, so swapping a model is a one-line change in `config.py`.

## Example output

```
Question: In three sentences, what should a company check before deploying an AI
                          assistant to its customers?
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ anthropic/claude-sonnet-5.5           ┃ mistralai/mistral-large-4-0          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Before deploying, a company should    │ Before deploying an AI assistant, a  │
│ test the assistant thoroughly for     │ company should verify its accuracy   │
│ accuracy, safety, and bias using      │ and relevance against up-to-date     │
│ realistic customer scenarios,         │ company information while ensuring   │
│ including edge cases and attempts to  │ it is free from harmful biases. It   │
│ misuse it, to ensure it gives         │ must also confirm that robust data   │
│ reliable answers and doesn't produce  │ privacy, security, and regulatory    │
│ harmful or off-brand content. It      │ compliance measures are in place to  │
│ should also verify that data privacy, │ protect customer data. Finally, the  │
│ security, and legal compliance        │ company should establish clear human │
│ requirements (such as GDPR or         │ escalation protocols and thoroughly  │
│ industry-specific regulations) are    │ test the system to handle edge cases │
│ met, including how customer data is   │ and complex inquiries gracefully.    │
│ collected, stored, and used. Finally, │                                      │
│ it should set up clear escalation     │                                      │
│ paths to human agents, transparent    │                                      │
│ disclosure that customers are talking │                                      │
│ to an AI, and ongoing monitoring so   │                                      │
│ problems can be caught and corrected  │                                      │
│ after launch.                         │                                      │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ Time: 2.74 s                          │ Time: 7.72 s                         │
│ Tokens: 34 in / 207 out / 241 total   │ Tokens: 21 in / 506 out / 527 total  │
└───────────────────────────────────────┴──────────────────────────────────────┘
```

**What this single run shows** (one question is not a benchmark, but it illustrates the trade-offs):

- **Quality:** both cover testing, privacy/compliance and human escalation. Claude adds AI disclosure and post-launch monitoring; Mistral is more concise.
- **Speed:** Claude answered in about a third of the time.
- **Tokens:** the same question counts as 34 input tokens for Claude but 21 for Mistral, because each provider splits text into tokens differently, so token counts are not directly comparable across providers.
  Mistral also reports more than twice the output tokens for a *shorter* visible answer, most likely
  because it reasons internally before replying, and those hidden tokens are billed too. This is exactly the kind of cost
  surprise a side-by-side test catches before a deployment.

## How to run it

**You need:** [uv](https://docs.astral.sh/uv/) (a Python project manager) and an
[OpenRouter API key](https://openrouter.ai/keys).

1. Clone the repository and enter the folder:
   ```
   git clone https://github.com/mattrogy/hello-openrouter.git
   cd hello-openrouter
   ```
2. Create a file named `.env` in the folder with your key:
   ```
   OPENROUTER_API_KEY=your-key-here
   ```
   This file is listed in `.gitignore`, so the key is never uploaded to GitHub.
3. Run it with the default question:
   ```
   uv run hello-openrouter
   ```
   Or ask your own question:
   ```
   uv run hello-openrouter "Explain retrieval-augmented generation in two sentences"
   ```

`uv` installs Python 3.12 and the dependencies automatically on the first run.

## Changing the models

Edit the `MODELS` list in [`src/hello_openrouter/config.py`](src/hello_openrouter/config.py).
Model IDs are listed at [openrouter.ai/models](https://openrouter.ai/models).

## Error handling

The tool gives plain-English messages instead of technical errors:

| Problem | What you see |
|---|---|
| No key in `.env` | "Missing API key. Add a line OPENROUTER_API_KEY=..." and the tool stops |
| Key rejected | "Your API key was rejected..." |
| Wrong or retired model ID | "Model '...' is not available on OpenRouter..." |
| No internet | "Could not reach OpenRouter..." |
| Out of credits / rate limit | "Rate limit reached or out of credits..." |

If one model fails, the other model's answer is still shown.

## Project structure

```
src/hello_openrouter/
  config.py      settings: OpenRouter address, model IDs, default question
  main.py        the tool: reads the question, calls each model, prints the table
DECISIONS.md     the main technical choices, the alternatives, and why
```

## Built with

Python 3.12 · [OpenAI Python SDK](https://github.com/openai/openai-python) (OpenRouter uses the same API format) ·
[python-dotenv](https://github.com/theskumar/python-dotenv) · [rich](https://github.com/Textualize/rich)
