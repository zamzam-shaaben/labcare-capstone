# LabCare — Multi-Agent Laboratory Concierge (Capstone)

 All prices, opening hours, patients, result summaries, and appointment slots are invented. No real laboratory is connected.

## What it does

- Pricing Agent: 5 example laboratory tests, USD prices and sample preparations.
- Information Agent: fictional opening hours and address.
- Appointment Agent: checks availability; booking requires a separate human confirmation button.
- Results Agent: requires report ID **and** private code; only released demo summaries are shown.
- Supervisor: routes questions to specialized LangGraph agents; Ollama generates grounded replies.
- Function calling: the agents ask for the read-only tools (prices, hours, slots) themselves; the tool schemas come from the MCP server.
- Memory: the last 6 chat turns are passed to the supervisor and agents, so follow-ups such as `and TSH?` work.
- MCP server: separate local process with tools for prices, hours, slots, bookings and report checks.
- Supports English and Arabic questions (model quality varies); a deterministic model-off mode is available.

## Architecture

```text
Streamlit UI -> LangGraph Supervisor -> Pricing / Information / Appointment / Results / General agent
                                   -> MCP Client (stdio) -> FastMCP Server -> SQLite demo database
                                   -> Ollama for grounded natural-language answers
```

The supervisor chooses a single specialist per question (sequential handoff). Each specialist is given a small allow-list of **read-only** MCP tools and the model decides, by function calling, which to call and with what arguments (for example `get_test_prices(query="TSH")`). If the model makes no tool call, the agent fetches its default tool in Python so the reply is still grounded in tool data.

The two consequential tools, `create_appointment` and `get_report_status`, are **never offered to the model**, and the allow-list is checked again in code before any call is executed. This is a deliberate safeguard: LLM output cannot book an appointment or open a report. The results tool can only be invoked from a code-entry form; booking happens only after a separate confirmation click.

| Agent | Tools the model may call |
|---|---|
| Pricing | `get_test_prices` |
| Information | `get_opening_hours` |
| Appointment | `list_appointment_slots`, `get_test_prices` |
| General | all three read-only tools |
| Results | none (fixed reply pointing to the secure form) |

## Requirements

- Python **3.11 or 3.12**
- Ollama installed and running, if using AI-generated chat responses
- A model with tool-calling support. The default is `qwen2.5:7b`; to use another one, set `OLLAMA_MODEL` before starting (PowerShell: `$env:OLLAMA_MODEL = 'gemma4:e4b'`)
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

1. Ask `How much is CBC?` or `كم سعر فحص TSH؟` → Pricing Agent. Follow with `and TSH?` → answered from conversation memory.
2. Ask `When are you open?` → Information Agent.
3. Ask `I need an appointment` → Appointment Agent, shows demo slots. Expand the booking form, review summary, confirm.
4. Expand **Check a demo report** and enter `DEMO-1001` + `472915` → released (fictional); `DEMO-1002` + `831264` → pending.
5. Enter a wrong code → access denied. Try two bookings in the same slot then a third → capacity refusal.

To reset sample data (and appointments), stop the app and delete `lab_demo.sqlite3`.

## Automated verification

```bash
python -m pytest -q
```

`pytest` uses a fresh temporary SQLite database and does not need Ollama. `tests/test_services.py` covers prices, working hours, inventory of time slots, explicit confirmation, capacity, invalid booking inputs, unauthorized result access, pending results and router examples. `tests/test_agents.py` runs the agents against the real MCP server with a scripted fake model: it checks that a model tool call reaches MCP, that a model asking for `create_appointment` or `get_report_status` is refused, that conversation history reaches the model, and that follow-up questions are routed. Live model response quality is not asserted by unit tests; use the manual cases under "Reproduce a demo".

## Project structure

```text
app.py                        Streamlit UI + explicit confirmation forms
lab_agents/agents.py          LangGraph supervisor / four specialists / general agent, function calling, memory
lab_agents/routing.py         Keyword intent router with follow-up handling
lab_agents/mcp_server.py      MCP tool declarations
lab_agents/service.py         Deterministic business rules
lab_agents/database.py        SQLite schema and demo seed data
tests/test_services.py        Automated checks of the business rules
tests/test_agents.py          Automated checks of tool calling, the allow-list and memory
```

## Safety / limitations

No real health record integration, identity verification, email/SMS delivery or real appointments. Demo access code is **not production authentication**. Storing a real patient access code in chat history is avoided by a separate password field, but this demo lacks full audit logs, encryption, rate limiting, consent, legal compliance, and secure deployment. Do not put real patient data in this prototype. No medical diagnosis or treatment recommendations are provided. Model mistakes in Arabic intent recognition remain possible. Prompts embedded in user input are treated as untrusted.
