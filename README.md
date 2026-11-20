# HCL IT Incident Diagnosis and Self-Healing System

Takes a free-text IT ticket and returns classification, priority, assignment, a suggested resolution and similar past tickets. It also checks whether a (test) service is down, proposes an allowlisted fix, waits for human approval, runs it, and verifies the result.

## Architecture

| Piece | Where | Role |
|---|---|---|
| `index.html` | Local file in the browser | Ticket form, results, Recovery card, Approve button |
| Ticket assistant backend | FastAPI, port 8000 | Supervisor and agents, SSE streaming, approve endpoint |
| Demo Internal App | `test_service/demo_app.py`, port 9000 | Fake company app that is deliberately stopped and restarted |

**Pipeline** (`agents/supervisor_agent.py`): retrieval, classification, priority, assignment, resolution, then diagnostics and recovery detection. The final SSE event carries the result, including a `recovery` proposal.

**Stack:** FastAPI, LangChain, FAISS over 10,888 historical tickets, BAAI/bge-small-en-v1.5 embeddings, Groq (`openai/gpt-oss-120b`), plain HTML frontend.

## Self-healing flow (RecoveryAgent)

1. Keyword gate decides whether a ticket may be an outage.
2. Real health check on `http://127.0.0.1:9000/health`.
3. If down, the agent **proposes** `restart_demo_service`. Nothing runs yet.
4. A person clicks **Approve & Run Recovery**.
5. `POST /api/recovery/approve` runs the action, then polls `/health` for up to 15 seconds.
6. The card shows **Recovered and verified** only if the service really answered HTTP 200. Otherwise it says to escalate.
7. Every step is logged to `backend/logs/recovery_actions.log`.

**Safety design:** only predefined actions with fixed commands are allowed (never LLM-generated commands), anything outside the allowlist is refused, and the target is a local test service.

## Setup

1. Create a venv (Python 3.13) and install `backend/requirements.txt`.
2. Copy `.env.example` to `.env` and add your Groq API key.
3. **Rebuild the vector store** after a fresh clone. `vectorstore/tickets_metadata.parquet` is no longer tracked in Git. Use `embedding_pipeline/build_index.py`.
4. Start the backend (PowerShell):

```
cd backend
$env:PYTHONPATH = "<path to project root>"
uvicorn app.main:app --reload
```

Wait for `Application startup complete.` (about 20 to 30 seconds).

5. Open `index.html` in the browser (Ctrl+F5 after edits).

## Demo script

1. Make sure port 9000 is down: `http://127.0.0.1:9000/health` should not load.
2. Submit: Subject `Internal application is not responding`, Description `I cannot access the application. It appears to be unavailable.`
3. The Self-Healing Recovery card shows the problem, the error text and the proposed action.
4. Click **Approve & Run Recovery**. Within 15 seconds the card says **Recovered and verified (HTTP 200)**.
5. Optional failure demo: stop the service, run `python -m http.server 9000 --bind 127.0.0.1` to block the port, submit the ticket and approve. The card says to escalate.
6. Show `backend/logs/recovery_actions.log` as the audit trail.

## Limitations

This is a proof of concept. One toy service, one action, keyword-based detection. In production the restart command would be replaced by the company's own tooling, such as a service-management API.

- **No authentication on Approve.** Anyone who can reach the page or endpoint can approve, and CORS is open. Fine for a local demo, not for production. The fix is an authorized approver with the identity recorded in the log.
- The log writes `approved` before the allowlist check, so a refused action still shows an `approved` line. The `outcome` line carries the refusal.
- The keyword gate is broad. Words like "service" or "down" trigger a health check, but a proposal appears only if the demo app is actually down.
- The restarted service is a background process that survives the backend stopping.
- The diagnostics card only proves the server machine has internet access. It says nothing about a VPN or a specific app.
- Classification and priority quality is limited. A VPN ticket came back as "Customer Service" with priority "Low", and the outage ticket as "IT Support / Bug" at 40% confidence. Accuracy has not been measured.
- RAG-mode resolutions can contain `<name>` and `<tel_num>` placeholders.
- When the 0.65 similarity filter finds nothing, the fallback shows "-" and 0%.
- Stale items: `llm_model_name` in `config.py`, old Phi-3 comments and packages (transformers, torch, accelerate) in `requirements.txt`.