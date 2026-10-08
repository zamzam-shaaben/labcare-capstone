# LabCare — Multi-Agent Laboratory Concierge (Capstone)

**Educational demonstration only.** All prices, opening hours, patients, result summaries, and appointment slots are invented. No real laboratory is connected.

## What it does

- Pricing Agent: 5 example laboratory tests, USD prices and sample preparations.
- Information Agent: fictional opening hours and address.
- Appointment Agent: checks availability; booking requires a separate human confirmation button.
- Results Agent: requires report ID **and** private code; only released demo summaries are shown.
- Supervisor: routes questions to specialized LangGraph agents; Ollama generates grounded replies.
- MCP server: separate local process with tools for prices, hours, slots, bookings and report checks.
- Supports English and Arabic questions (model quality varies); a deterministic model-off mode is available.

## Architecture

```text
Streamlit UI -> LangGraph Supervisor -> Pricing / Information / Appointment / Results / General agent
                                   -> MCP Client (stdio) -> FastMCP Server -> SQLite demo database
                                   -> Ollama for grounded natural-language answers
```

The supervisor chooses a single specialist per question (sequential handoff). For the tiny prototype, **the agents explicitly select the MCP tools in Python**, instead of allowing an LLM to autonomously execute arbitrary tools. This is a deliberate safeguard: LLM output cannot directly execute sensitive actions. The results tool can only be invoked from a code-entry form; booking happens only after a separate confirmation click.

## Requirements

- Python **3.11 or 3.12**
- Ollama installed and running, if using AI-generated chat responses
- Windows PowerShell / macOS / Linux terminal

## Run (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull qwen2.5:7b
ollama serve  # in another terminal; if Ollama is already running, skip
streamlit run app.py
```

## Run (macOS / Linux)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen2.5:7b
ollama serve # another terminal unless already running
streamlit run app.py
```

Open the Streamlit local URL printed in the terminal (usually http://localhost:8501). If hardware cannot run the model, toggle **Use local Ollama** off: all demo tools and bookings still function.

To run the MCP server alone: `python -m lab_agents.mcp_server` (stdio protocol, not a browser page).

## Reproduce a demo

1. Ask `How much is CBC?` or `كم سعر فحص TSH؟` → Pricing Agent.
2. Ask `When are you open?` → Information Agent.
3. Ask `I need an appointment` → Appointment Agent, shows demo slots. Expand the booking form, review summary, confirm.
4. Expand **Check a demo report** and enter `DEMO-1001` + `472915` → released (fictional); `DEMO-1002` + `831264` → pending.
5. Enter a wrong code → access denied. Try two bookings in the same slot then a third → capacity refusal.

To reset sample data (and appointments), stop the app and delete `lab_demo.sqlite3`.

## Automated verification

```bash
python -m pytest -q
```

`pytest` uses a fresh temporary SQLite database. The tests cover prices, working hours, inventory of time slots, explicit confirmation, capacity, invalid booking inputs, unauthorized result access, pending results and router examples. Live model response quality is not asserted by unit tests; manual cases appear in `docs/evaluation.md`.

## Project structure

```text
app.py                        Streamlit UI + explicit confirmation forms
lab_agents/agents.py          LangGraph supervisor / four specialists / general agent
lab_agents/mcp_server.py      MCP tool declarations
lab_agents/service.py         Deterministic business rules
lab_agents/database.py        SQLite schema and demo seed data
tests/test_services.py        Automated checks
docs/evaluation.md            Test plan, observations and risks
```

## Safety / limitations

No real health record integration, identity verification, email/SMS delivery or real appointments. Demo access code is **not production authentication**. Storing a real patient access code in chat history is avoided by a separate password field, but this demo lacks full audit logs, encryption, rate limiting, consent, legal compliance, and secure deployment. Do not put real patient data in this prototype. No medical diagnosis or treatment recommendations are provided. Model mistakes in Arabic intent recognition remain possible. Prompts embedded in user input are treated as untrusted.

## Publish to GitHub

Create an empty **private or public** repository on github.com, then from this project folder:

```bash
git init
git add .
git commit -m "Initial LabCare multi-agent capstone"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/labcare-capstone.git
git push -u origin main
```

Replace `YOUR_USERNAME`. Verify `.gitignore` excludes `.env`, SQLite data and venv. Add your real repo URL to the report before submitting. We cannot publish to your GitHub account from this archive.
