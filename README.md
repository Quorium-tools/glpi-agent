# GLPI LLM Agent

Command-line assistant that uses an OpenRouter model to read and update GLPI through the official GLPI API V2.

OpenRouter is connected in this project. The LLM receives your prompt, decides which GLPI tool to use, and the local Python code executes the real GLPI API call.

| Agent | Audience | Route |
|-------|----------|-------|
| **IT Admin Agent** | IT technicians — full GLPI access | `/` |
| **Knowledge Base Agent** | Non-IT staff (Finance, HR, Legal) — self-service tickets | `/knowledge-base` |

## Quick Start

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o-mini

GLPI_BASE_URL=https://your-glpi.example.com
GLPI_API_VERSION=v2.3

GLPI_OAUTH_CLIENT_ID=client_id_from_glpi
GLPI_OAUTH_CLIENT_SECRET=client_secret_from_glpi
GLPI_OAUTH_SCOPE=api
GLPI_USERNAME=your_glpi_username
GLPI_PASSWORD=your_glpi_password
```

Check the active config without printing secrets:

```bash
python -m glpi_agent.cli --show-config

python -m glpi_agent.cli_knowledge_base_agent --show-config
```

Run one prompt:

```bash
python -m glpi_agent.cli "Show me the 10 newest tickets with their ID, title, status, and priority."

python -m glpi_agent.cli_knowledge_base_agent "How do I connect to VPN?"
```

Start interactive mode:

```bash
python -m glpi_agent.cli

python -m glpi_agent.cli_knowledge_base_agent
```

## What You Need

- Python 3.10 or newer.
- An OpenRouter API key.
- A GLPI server with API access enabled.
- A GLPI OAuth client under `Setup > OAuth Clients`.
- A GLPI username/password allowed to use the API.

## How It Works

### Request flow (both agents)
The flow is:

1. `python -m glpi_agent.cli` / `python -m glpi_agent.cli_knowledge_base_agent` - starts the CLI.
2. `glpi_agent/config.py` loads `.env`.
3. `glpi_agent/cli.py` / `glpi_agent/cli_knowledge_base_agent.py`creates the OpenRouter client.
4. `glpi_agent/openrouter_client.py` sends the prompt and tool definitions to OpenRouter.
5. OpenRouter returns either a normal answer or a tool call.
6. `glpi_agent/agent.py` / `glpi_agent/knowledge_base_agent.py` validates and executes the requested local tool.
7. `glpi_agent/glpi_client.py` authenticates with GLPI OAuth and calls GLPI API V2.
8. The GLPI result is sent back to OpenRouter so it can answer in normal language.

The LLM does not call GLPI directly. It can only request the tools exposed in `glpi_agent/agent.py` / `glpi_agent/knowledge_base_agent.py` .

## Project Files

```text
glpi_agent/
  cli.py                CLI entrypoint and flags.
  config.py             Loads .env and validates required settings.
  openrouter_client.py  Sends chat/tool requests to OpenRouter.
  agent.py              System prompt, tools, and tool-call loop.
  cli_knowledge_base_agent.py     Agent 2 entrypoint — same structure as cli.py
  knowledge_base_agent.py         Agent 2 — system prompt, 6 tool schemas, local KB fiches
  glpi_client.py        GLPI OAuth, item paths, ticket status mapping, API calls.
  http_json.py          Small urllib JSON/form request helper.
.env.example            Environment variable template.
EXAMPLES.md             More copy-paste commands and prompts.
README.md               Main runbook.
```

## OpenRouter Settings

Required:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

Optional:

```bash
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Override the model for one run:

```bash
python -m glpi_agent.cli --model anthropic/claude-3.5-sonnet "Show me the 5 newest tickets"

python -m glpi_agent.cli_knowledge_base_agent --model anthropic/claude-3.5-sonnet "How do I reset my password?"
```

## GLPI OAuth Setup

In GLPI:

1. Enable the API.
2. Go to `Setup > OAuth Clients`.
3. Create an OAuth client.
4. Allow the `Password` grant.
5. Allow the `api` scope.
6. Put the client ID and secret in `.env`.

The agent requests a token from:

```text
{GLPI_BASE_URL}/api.php/token
```

Then it calls GLPI API V2 routes under:

```text
{GLPI_BASE_URL}/api.php/{GLPI_API_VERSION}
```

Example ticket route:

```text
{GLPI_BASE_URL}/api.php/v2.3/Assistance/Ticket
```
## Agent 1 — IT Admin Agent

Full GLPI access for IT technicians. Translates natural language into 20+ GLPI API V2 operations.


## CLI Commands

Show config:

```bash
python -m glpi_agent.cli --show-config
```

Run one prompt:

```bash
python -m glpi_agent.cli "List the supported GLPI item types."
```

Ticket CRUD examples:

```bash
python -m glpi_agent.cli "Create a fake test ticket titled 'Fix Docker dependencies' and generate harmless test details."
python -m glpi_agent.cli "List my newest tickets."
python -m glpi_agent.cli "Show ticket 12."
python -m glpi_agent.cli "Update ticket 12 priority to high and status to processing."
python -m glpi_agent.cli "Set ticket 12 opening date to 2026-05-19 13:13:23, type incident, request source ID 1, urgency medium, impact medium, priority low, total duration 30 minutes, and external ID EXT-12."
python -m glpi_agent.cli "Set ticket 12 requester user ID 4, observer user ID 8, and assigned user ID 2."
python -m glpi_agent.cli "Delete ticket 12. I confirm deleting ticket 12."
```

Support suggestion examples:

```bash
python -m glpi_agent.cli "Suggest a solution for ticket 12."
python -m glpi_agent.cli "Add that solution to ticket 12 and mark it solved."
```

Run with a different model:

```bash
python -m glpi_agent.cli --model openai/gpt-4o-mini "Show me the 5 newest tickets"
```

Interactive mode:

```bash
python -m glpi_agent.cli
```

## Web Chat Frontend

A Next.js chat UI in `frontend/` serves both agents from a single API route (`frontend/app/api/chat/route.ts`).

```bash
cd frontend
npm install
npm run dev
```

| URL | Agent | Features |
|-----|-------|----------|
| `http://localhost:3003` | IT Admin Agent | Model override, quick prompts |
| `http://localhost:3003/knowledge-base` | Knowledge Base Agent | Model override, quick prompts |

```text
http://localhost:3003
```

The web UI includes:

- a modern chat surface
- quick prompt buttons
- live GLPI writes by default
- an optional OpenRouter model override
- Enter-to-send support

The frontend API route runs:

```bash
python -m glpi_agent.cli
```

from the project root, so it reuses the same `.env` file as the CLI.
Both UIs send requests to `/api/chat` with an `agent` field (`"admin"` or `"knowledge-base"`). The route dispatches to the correct Python CLI or Docker backend automatically.

## Run With Docker Compose

The compose setup starts three services with live-mounted source code:

- `ticket-agent`: Ticket/Admin Agent HTTP API on `http://localhost:8003`
- `knowledge-agent`: Knowledge Base Agent HTTP API on `http://localhost:8004`
- `frontend`: Next.js chat UI on `http://localhost:3003`

The mounted paths are:

```text
./glpi_agent -> /app/glpi_agent
./frontend   -> /app
```

Frontend changes reload through `next dev`. Backend changes are picked up on the next request because both backends run the mounted Python code in a fresh subprocess during development.

Create and fill `.env` first:

```bash
cp .env.example .env
```

Then run:

```bash
./run.sh
```

Useful script commands:

```bash
./run.sh start     # start all agents and frontend in the background
./run.sh dev       # start in the foreground with live logs
./run.sh stop      # stop containers
./run.sh restart   # rebuild and restart
./run.sh logs      # follow logs
./run.sh status    # show running containers
./run.sh ticket    # follow Ticket Agent logs
./run.sh knowledge # follow Knowledge Base Agent logs
```

Or directly:

```bash
docker compose up --build
```

The frontend routes requests to each backend:

```text
BACKEND_URL=http://ticket-agent:8003
BACKEND_KB_URL=http://knowledge-agent:8004
```

Health endpoints:

```bash
curl http://localhost:8003/health
curl http://localhost:8004/health   # Knowledge Base Agent
```

## Available Tools

The OpenRouter model can only choose from these tools:

| Tool | Purpose |
| --- | --- |
| `list_supported_itemtypes` | Shows supported friendly GLPI item names and ticket statuses. |
| `list_items` | Lists one page of items like tickets, computers, users, printers, and software. |
| `list_all_items` | Fetches paginated results up to a safe maximum when you ask for all items. |
| `get_item` | Gets one GLPI item by type and ID. |
| `search_items` | Searches GLPI items with a V2 RSQL filter. |
| `list_tickets` | Lists tickets in a compact summary format. |
| `get_ticket` | Gets one ticket by ID with useful context. |
| `create_ticket` | Creates a ticket. |
| `create_problem` | Creates a problem record for recurring/root-cause issues. |
| `create_change` | Creates a change record for planned work. |
| `create_asset` | Creates assets such as computers, printers, phones, monitors, network equipment, peripherals, or software. |
| `create_knowledge_base_item` | Creates a knowledge base article/item. |
| `update_item` | Updates fields on a GLPI item. |
| `update_ticket` | Updates ticket title, content, opening date, type, category, status, request source, urgency, impact, priority, total duration, external ID, location, actors, or raw fields. |
| `update_ticket_fields` | Updates urgency, impact, priority, category, request source, location, total duration, external ID, or raw ticket fields. |
| `update_ticket_status` | Updates a ticket status with names like `pending`, `solved`, or `closed`. |
| `update_ticket_actors` | Updates requester, observer, and assigned user/group actors. |
| `assign_ticket_user` | Assigns a ticket to a user/technician ID. |
| `assign_ticket_group` | Assigns a ticket to a group ID. |
| `add_ticket_followup` | Adds a follow-up/comment to a ticket. |
| `add_ticket_task` | Adds a technical task/worklog to a ticket. |
| `add_ticket_solution` | Adds a solution/resolution to a ticket and can mark it solved. |
| `suggest_ticket_solution` | Fetches ticket context so the agent can draft a solution without saving it. |
| `link_ticket_item` | Links an asset or GLPI item to a ticket. |
| `delete_ticket` | Deletes a ticket after explicit confirmation for the exact ticket ID. |
| `ticket_report` | Builds a summary report by status, priority, urgency, impact, and oldest open tickets. |

Agent guards:

- The agent is restricted to GLPI ticket/support work only.
- Out-of-scope questions are refused with a short ticket-scope message.
- GLPI data is treated as untrusted text, so instructions inside tickets are ignored.
- Secrets, tokens, passwords, and authorization values are redacted from tool results and errors.
- Ticket updates must use ticket-specific tools instead of generic item updates.
- Delete, close, solve, and purge-style actions require the exact ticket ID in the user request.
- The agent does not save a suggested solution unless the user explicitly asks to add or save it.

Common item type mappings:

```text
Ticket -> Assistance/Ticket
Computer -> Assets/Computer
User -> Administration/User
Group -> Administration/Group
ITILCategory -> Dropdowns/ITILCategory
RequestType / RequestSource -> Dropdowns/RequestType
Location -> Dropdowns/Location
Printer -> Assets/Printer
Software -> Assets/Software
Problem -> Assistance/Problem
Change -> Assistance/Change
KnowledgeBase -> Tools/KnowbaseItem
```

For unsupported resources, use the full GLPI V2 path:

```text
List Assets/Computer items.
Get Administration/User 5.
```

Ticket status names supported by the helper:

```text
new, approval, processing assigned, processing planned, pending, solved, closed
```

Ticket type names supported by the helper:

```text
incident, request
```

Priority, urgency, and impact names supported by the helper:

```text
major, very high, high, medium, low, very low
```

## Examples To Try

Safe read-only examples:

```bash
python -m glpi_agent.cli "What can you do with GLPI?"
```

```bash
python -m glpi_agent.cli "List the supported GLPI item types."
```

```bash
python -m glpi_agent.cli "Show me the 10 newest tickets with their ID, title, status, and priority."
```

```bash
python -m glpi_agent.cli "Get ticket 12 and summarize the issue, requester, status, and latest notes if available."
```

```bash
python -m glpi_agent.cli "Search computers with name like laptop and show ID, name, serial number, and entity."
```

```bash
python -m glpi_agent.cli "Generate a ticket report grouped by status, priority, urgency, and impact."
```

Write examples:

```bash
python -m glpi_agent.cli "Create a low priority ticket titled 'Keyboard replacement request' with content 'User needs a replacement keyboard for workstation HR-04.'"
```

```bash
python -m glpi_agent.cli "Add a follow-up to ticket 12 saying: Waiting for user confirmation after password reset."
```

```bash
python -m glpi_agent.cli "Set ticket 12 status to solved."
```

Delete examples:

```bash
python -m glpi_agent.cli "Delete ticket 12. I confirm deleting ticket 12."
```

## Agent 2 — Knowledge Base Agent

Self-service IT support for non-IT departments. Handles three tiers automatically:

| Tier | Trigger | Action |
|------|---------|--------|
| **1 — KB Answer** | Issue matches a local fiche or solved ticket (confidence ≥ 0.8) | Returns solution directly |
| **2 — Ticket** | No match found | Creates GLPI ticket immediately |
| **3 — Emergency** | Message contains `URGENT`, `CRITICAL`, or `EMERGENCY` | Returns Help Desk phone number |

IT staff are rejected automatically if their email prefix matches known IT patterns (`tech.`, `admin.`, `it.`, `dsi.`, etc.).

### CLI

```bash
# One-shot
python -m glpi_agent.cli_knowledge_base_agent "How do I connect to VPN?"

# With user email (enables IT staff check)
python -m glpi_agent.cli_knowledge_base_agent --user-email "jean.dupont@cd08.fr" "I can't access SEDIT."

# Override model
python -m glpi_agent.cli_knowledge_base_agent --model openai/gpt-4o "How do I reset my password?"

# Interactive REPL
python -m glpi_agent.cli_knowledge_base_agent
```

### Built-in Knowledge Base (Fiches CD08)

Seven fiches are embedded in `knowledge_base_agent.py` and searched locally on every query:

| ID | Topic |
|----|-------|
| FICHE-001 | Windows password reset — self-service portal |
| FICHE-002 | VPN connection — Cisco AnyConnect |
| FICHE-003 | Outlook access from outside the office |
| FICHE-004 | Network printer problems |
| FICHE-005 | New user account creation request |
| FICHE-006 | SEDIT financial software access |
| FICHE-007 | Reporting a security incident |

The agent also searches GLPI solved and closed tickets using the keywords extracted from the user's message.

To add a new fiche: append an entry to `LOCAL_KB` in `knowledge_base_agent.py` with `id`, `title`, `keywords`, `solution`, and `source` fields.

---

More examples are in `EXAMPLES.md`.

## Feature Coverage

### Agent 1 — IT Admin

- Ticket lifecycle: create, list, search, update status, update fields, follow up, add task, add solution, delete with confirmation.
- Assignment: assign tickets to a user ID or group ID.
- Asset workflow: search/list/create assets and link an asset to a ticket.
- ITIL workflow: create problems and changes from recurring incidents or planned work.
- Knowledge base: search/list/create knowledge base items, depending on your GLPI endpoint availability.
- Users and groups: search/list users and groups before assignment.
- Reporting: summarize tickets by status, priority, urgency, impact, and oldest open tickets.

### Agent 2 — Knowledge Base (6 tools)

- **`search_knowledge_base`** — searches 7 embedded local fiches + GLPI solved/closed tickets; returns confidence-ranked results

- **`create_basic_ticket`** — creates a ticket with title, description, and priority

- **`get_support_contact`** — returns Help Desk phone and hours for URGENT/CRITICAL/EMERGENCY queries

- **`verify_non_it_user`** — rejects IT staff by email prefix or GLPI department before serving the user

- **`get_ticket_by_id`** — fetches ticket details and solution text from the Timeline endpoint

- **`log_unfound_query`** — logs queries that found no KB match, for Help Desk review

GLPI V2 exposes exact endpoint schemas through your server's Swagger docs:

```text
{GLPI_BASE_URL}/api.php/doc
```

If a tool returns a path/schema error for your GLPI Network Cloud version, compare the requested action with your `/api.php/doc` schema.

## Troubleshooting

`Missing required environment variables: OPENROUTER_API_KEY`

Add your OpenRouter key to `.env`.

`Missing required environment variables: GLPI_BASE_URL`

Set `GLPI_BASE_URL` to the root URL of your GLPI server, without `/api.php`.

`Set GLPI_OAUTH_CLIENT_ID...`

Add `GLPI_OAUTH_CLIENT_ID`, `GLPI_OAUTH_CLIENT_SECRET`, `GLPI_USERNAME`, and `GLPI_PASSWORD`.

`This project is configured for GLPI API V2`

Set `GLPI_API_VERSION=v2` or `GLPI_API_VERSION=v2.3`.

`HTTP 401` or `HTTP 403` from GLPI

Check the OAuth client, password grant, `api` scope, username/password, and GLPI permissions.

`HTTP 401` from OpenRouter

Check `OPENROUTER_API_KEY`.

`Invalid JSON body` when listing tickets

This usually means the API received a GET request with JSON-body headers or unsupported query parameters. The client avoids that by not sending `Content-Type: application/json` on bodyless GET requests and by using GLPI V2 collection parameters such as `start`, `limit`, `filter`, and `sort`.

`Unsupported GLPI V2 item type`

Use a supported friendly name like `Ticket`, `Computer`, or `User`, or pass a full GLPI V2 path like `Assets/Computer`.

## Safety Notes

- The model is restricted to the local tools listed in `agent.py`.
- The model is instructed not to invent ticket IDs or statuses.
- Ticket deletion requires explicit confirmation for the exact ticket ID.

## GLPI Docs

- https://help.glpi-project.org/documentation/modules/configuration/general/api/api
- https://help.glpi-project.org/documentation/modules/configuration/general/api/restful-api-v2
