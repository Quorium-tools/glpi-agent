# GLPI LLM Agent

Command-line assistant that uses an OpenRouter model to read and update GLPI through the official GLPI API V2.

OpenRouter is connected in this project. The LLM receives your prompt, decides which GLPI tool to use, and the local Python code executes the real GLPI API call.

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

GLPI_AGENT_DRY_RUN=false
```

Check the active config without printing secrets:

```bash
python -m glpi_agent.cli --show-config
```

Run one prompt:

```bash
python -m glpi_agent.cli "Show me the 10 newest tickets with their ID, title, status, and priority."
```

Start interactive mode:

```bash
python -m glpi_agent.cli
```

## What You Need

- Python 3.10 or newer.
- An OpenRouter API key.
- A GLPI server with API access enabled.
- A GLPI OAuth client under `Setup > OAuth Clients`.
- A GLPI username/password allowed to use the API.

## How It Works

The flow is:

1. `python -m glpi_agent.cli` starts the CLI.
2. `glpi_agent/config.py` loads `.env`.
3. `glpi_agent/cli.py` creates the OpenRouter client.
4. `glpi_agent/openrouter_client.py` sends the prompt and tool definitions to OpenRouter.
5. OpenRouter returns either a normal answer or a tool call.
6. `glpi_agent/agent.py` validates and executes the requested local tool.
7. `glpi_agent/glpi_client.py` authenticates with GLPI OAuth and calls GLPI API V2.
8. The GLPI result is sent back to OpenRouter so it can answer in normal language.

The LLM does not call GLPI directly. It can only request the tools exposed in `glpi_agent/agent.py`.

## Project Files

```text
glpi_agent/
  cli.py                CLI entrypoint and flags.
  config.py             Loads .env and validates required settings.
  openrouter_client.py  Sends chat/tool requests to OpenRouter.
  agent.py              System prompt, tools, and tool-call loop.
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

## CLI Commands

Show config:

```bash
python -m glpi_agent.cli --show-config
```

Run one prompt:

```bash
python -m glpi_agent.cli "List the supported GLPI item types."
```

Run with dry-run writes:

```bash
python -m glpi_agent.cli --dry-run "Create a ticket for a broken printer"
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

A Next.js chat UI is available in `frontend/`. It calls the existing Python agent through the local API route `frontend/app/api/chat/route.ts`.

Install and run it:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

The web UI includes:

- a modern chat surface
- quick prompt buttons
- a dry-run toggle, enabled by default
- an optional OpenRouter model override
- Enter-to-send support

The frontend API route runs:

```bash
python -m glpi_agent.cli
```

from the project root, so it reuses the same `.env` file as the CLI.

## Dry Run Mode

Use dry run before testing prompts that create or update GLPI data:

```bash
python -m glpi_agent.cli --dry-run "Set ticket 12 status to solved."
```

Or with an environment variable:

```bash
GLPI_AGENT_DRY_RUN=true python -m glpi_agent.cli "Create a ticket for a broken printer"
```

Dry run returns the method, URL, and payload instead of sending write requests to GLPI.

Read operations still call GLPI.

## Available Tools

The OpenRouter model can only choose from these tools:

| Tool | Purpose |
| --- | --- |
| `list_supported_itemtypes` | Shows supported friendly GLPI item names and ticket statuses. |
| `list_items` | Lists one page of items like tickets, computers, users, printers, and software. |
| `list_all_items` | Fetches paginated results up to a safe maximum when you ask for all items. |
| `get_item` | Gets one GLPI item by type and ID. |
| `search_items` | Searches GLPI items with a V2 RSQL filter. |
| `create_ticket` | Creates a ticket. |
| `create_problem` | Creates a problem record for recurring/root-cause issues. |
| `create_change` | Creates a change record for planned work. |
| `create_asset` | Creates assets such as computers, printers, phones, monitors, network equipment, peripherals, or software. |
| `create_knowledge_base_item` | Creates a knowledge base article/item. |
| `update_item` | Updates fields on a GLPI item. |
| `update_ticket_fields` | Updates urgency, impact, priority, category, location, or raw ticket fields. |
| `update_ticket_status` | Updates a ticket status with names like `pending`, `solved`, or `closed`. |
| `assign_ticket_user` | Assigns a ticket to a user/technician ID. |
| `assign_ticket_group` | Assigns a ticket to a group ID. |
| `add_ticket_followup` | Adds a follow-up/comment to a ticket. |
| `add_ticket_task` | Adds a technical task/worklog to a ticket. |
| `add_ticket_solution` | Adds a solution/resolution to a ticket and can mark it solved. |
| `link_ticket_item` | Links an asset or GLPI item to a ticket. |
| `delete_ticket` | Deletes a ticket after explicit confirmation for the exact ticket ID. |
| `ticket_report` | Builds a summary report by status, priority, urgency, impact, and oldest open tickets. |

Common item type mappings:

```text
Ticket -> Assistance/Ticket
Computer -> Assets/Computer
User -> Administration/User
Group -> Administration/Group
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
new, incoming, processing, assigned, planned, pending, waiting, solved, resolved, closed
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

Dry-run write examples:

```bash
python -m glpi_agent.cli --dry-run "Create a ticket titled 'Printer blocked in accounting' with content 'The accounting printer is blocked and users cannot print invoices.' Priority high."
```

```bash
python -m glpi_agent.cli --dry-run "Add a follow-up to ticket 12 saying: The technician checked the switch port and found no physical issue."
```

```bash
python -m glpi_agent.cli --dry-run "Set ticket 12 status to pending."
```

```bash
python -m glpi_agent.cli --dry-run "Mark ticket 12 as solved."
```

```bash
python -m glpi_agent.cli --dry-run "Add a task to ticket 12: checked the switch port and printer queue, duration 30 minutes."
```

```bash
python -m glpi_agent.cli --dry-run "Resolve ticket 12 with solution: replaced toner and printed a test page."
```

```bash
python -m glpi_agent.cli --dry-run "Set ticket 12 urgency to 5, impact to 4, and priority to 5."
```

```bash
python -m glpi_agent.cli --dry-run "Assign ticket 12 to user ID 2."
```

```bash
python -m glpi_agent.cli --dry-run "Assign ticket 12 to group ID 3."
```

```bash
python -m glpi_agent.cli --dry-run "Create a printer asset named HP Accounting Printer with serial number ACC-HP-001."
```

```bash
python -m glpi_agent.cli --dry-run "Link ticket 12 to printer ID 4."
```

```bash
python -m glpi_agent.cli --dry-run "Create a problem titled 'Repeated VPN outages' with content 'Remote users report repeated VPN disconnects every morning.'"
```

```bash
python -m glpi_agent.cli --dry-run "Create a change titled 'Upgrade office firewall firmware' with content 'Planned firmware upgrade to address VPN instability.'"
```

```bash
python -m glpi_agent.cli --dry-run "Create a knowledge base article titled 'How to reset VPN access' with content 'Steps for first-line support to reset VPN access.'"
```

Real write examples:

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
python -m glpi_agent.cli --dry-run "Delete ticket 12. I confirm deleting ticket 12."
```

```bash
python -m glpi_agent.cli "Delete ticket 12. I confirm deleting ticket 12."
```

Permanent purge is stronger than normal delete. Only use it when you really want GLPI to purge the ticket:

```bash
python -m glpi_agent.cli --dry-run "Permanently purge ticket 12. I confirm permanently purging ticket 12."
```

More examples are in `EXAMPLES.md`.

## Feature Coverage

The agent now covers these GLPI workflows through API tools:

- Ticket lifecycle: create, list, search, update status, update fields, follow up, add task, add solution, delete with confirmation.
- Assignment: assign tickets to a user ID or group ID.
- Asset workflow: search/list/create assets and link an asset to a ticket.
- ITIL workflow: create problems and changes from recurring incidents or planned work.
- Knowledge base: search/list/create knowledge base items, depending on your GLPI endpoint availability.
- Users and groups: search/list users and groups before assignment.
- Reporting: summarize tickets by status, priority, urgency, impact, and oldest open tickets.

GLPI V2 exposes exact endpoint schemas through your server's Swagger docs:

```text
{GLPI_BASE_URL}/api.php/doc
```

If a tool returns a path/schema error for your GLPI Network Cloud version, test the same prompt with `--dry-run` and compare the generated URL/payload with your `/api.php/doc` schema.

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
- Use `--dry-run` before testing create/update prompts.

## GLPI Docs

- https://help.glpi-project.org/documentation/modules/configuration/general/api/api
- https://help.glpi-project.org/documentation/modules/configuration/general/api/restful-api-v2
