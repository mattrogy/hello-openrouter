# Decisions

A log of the main technical choices in this project: what was chosen, what else was possible, and why.

## 1. OpenRouter instead of calling Anthropic and Mistral directly
- **Choice:** one OpenRouter account and key reaches both providers.
- **Alternatives:** the Anthropic API and the Mistral API, each with its own SDK and key.
- **Why:** one key, one bill, one code path. Switching models means changing a string, not
  rewriting the integration. The trade-off is a middleman: a small extra delay, and the data passes
  through one more company. An enterprise deployment with strict data rules might go direct.

## 2. The OpenAI Python SDK instead of raw HTTP requests
- **Choice:** the official `openai` package, pointed at `https://openrouter.ai/api/v1`.
- **Alternatives:** `requests`/`httpx` by hand, or each provider's own SDK.
- **Why:** OpenRouter uses the same API format as OpenAI, so the SDK works as is. It also gives
  typed errors (`AuthenticationError`, `NotFoundError`, ...) that make clear error messages easy.

## 3. The two models, and how they were chosen
- **Choice:** `anthropic/claude-sonnet-5.5` and `mistralai/mistral-large-4-0`.
- **Alternatives:** Claude Opus 5.5 (Anthropic's top model, slower and pricier), Claude Haiku 5.5
  (cheapest), Mistral Medium 3.5.
- **Why:** Sonnet is the usual default for business workloads and Mistral Large is Mistral's flagship,
  so the comparison is roughly like for like. The IDs were taken from OpenRouter's live models list
  (`https://openrouter.ai/api/v1/models`) on 2026-10-19 rather than guessed, because model IDs change
  often and a wrong ID fails at runtime.

## 4. All settings in `config.py`
- **Choice:** base URL, model IDs and default question live in one small file.
- **Alternatives:** hardcode them in the main code, or use command-line flags / environment variables.
- **Why:** anyone can change the models without reading the program logic. Command-line flags for
  models would be a natural next step.

## 5. Calling the models one after the other
- **Choice:** sequential calls.
- **Alternatives:** parallel calls with threads or `asyncio`, which finish faster in total.
- **Why:** simpler code, and each model's timing is measured on its own, without competing for the
  network. With only two models the extra wait is a few seconds.

## 6. `rich` for the side-by-side table
- **Choice:** the `rich` library.
- **Alternatives:** plain `print`, or `tabulate`.
- **Why:** long answers have to wrap inside their own column to be readable side by side. Doing that by
  hand with `print` is fiddly; `rich` does it in a few lines and handles any terminal width.

## 7. Error handling: one failure doesn't stop the comparison
- **Choice:** catch the SDK's typed errors per model and show a plain-English message in that model's column.
- **Alternatives:** let the program crash with a traceback, or stop at the first error.
- **Why:** if one model is down or renamed, you still see the other answer. A missing key is the one
  exception: it stops the program right away, because nothing can work without it.

## 8. Package layout (`src/hello_openrouter/`) with a `hello-openrouter` command
- **Choice:** kept the layout `uv init` created, and registered a `hello-openrouter` command in `pyproject.toml`.
- **Alternatives:** a single `main.py` at the project root, run with `uv run main.py`.
- **Why:** it behaves like a real command-line tool (`uv run hello-openrouter "question"`) and is the
  standard structure for Python projects, at the cost of one extra folder.

## 9. Python 3.12, managed by uv
- **Choice:** the project requires Python 3.12 or newer (`requires-python` in `pyproject.toml`, and
  `.python-version`), which `uv` downloads and manages itself.
- **Alternatives:** keep supporting macOS's built-in Python 3.9, which `uv` picked at first.
- **Why:** 3.9 no longer gets security fixes, and newer libraries are dropping it. Supporting both meant
  the lockfile carried two versions of `openai` (2.x for old Pythons, 3.x for new ones); requiring 3.12
  leaves one, so everyone who runs the project gets the same libraries.

## 10. Accepting `openai` 3.x and its new `httpx2` dependency (checked 2026-10-19)
- **Choice:** keep `openai` 3.35.1, which replaced `httpx`/`httpcore` with `httpx2`/`httpcore2` and also brought in `truststore`.
- **Alternatives:** pin `openai` below 3.0 to stay on the familiar `httpx`.
- **Why it was checked:** switching to Python 3.12 pulled in a new major version of `openai` and two
  packages whose names are one character away from well-known ones. Lookalike names are a common way
  to slip malware into a project, so they were checked before the tool was run.
- **What the check found:**
  - All four packages come from the official registry (`pypi.org`), according to `uv.lock`.
  - `openai` 3.35.1's metadata points to OpenAI's official repository (`github.com/openai/openai-python`),
    and it is `openai` itself that requires `httpx2`, so nothing was added by mistake.
  - On PyPI, `httpx2` and `httpcore2` are by Tom Christie (the original author of `httpx`), point to
    `github.com/pydantic/httpx2`, and have had 19 releases since May 2026. `truststore` is a dependency of `httpcore2`.
  - The installed `openai` 3.x still has everything this tool uses: the `OpenAI` client, the 7 error
    classes, the `status_code`/`message` fields and the token-count fields. No code change was needed,
    and a real run worked.
- **Limits of the check:** it looked at where the packages come from and who publishes them. It did not
  review their source code or confirm that PyPI uploads are built from those GitHub repositories. The
  `httpx2` version installed (2.14.0) was uploaded on 2026-10-18, only a day earlier. `uv.lock` records a
  hash for every file, so later installs get exactly these files or fail.
