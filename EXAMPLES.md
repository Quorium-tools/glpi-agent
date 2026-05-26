# GLPI Agent Examples

Use these after your `.env` is configured.

# Agent 1 — IT Admin Agent

## Check Configuration

```bash
python -m glpi_agent.cli --show-config
```

Try another OpenRouter model for one run:

```bash
python -m glpi_agent.cli --model anthropic/claude-3.5-sonnet "Show me the 5 newest tickets"
```

## Safe Read-Only Prompts

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
python -m glpi_agent.cli "List all tickets I have."
```

```bash
python -m glpi_agent.cli "Get ticket 12 and summarize the issue, requester, status, and latest notes if available."
```

```bash
python -m glpi_agent.cli "Search computers with name like laptop and show ID, name, serial number, and entity."
```

```bash
python -m glpi_agent.cli "List 10 printers and show their ID, name, location, and status."
```

```bash
python -m glpi_agent.cli "Find users with name like souhail and show the closest matches."
```

```bash
python -m glpi_agent.cli "List recent problems and summarize them as a table."
```

```bash
python -m glpi_agent.cli "Generate a ticket report grouped by status, priority, urgency, and impact."
```

```bash
python -m glpi_agent.cli "Search groups with name like support."
```

```bash
python -m glpi_agent.cli "Search knowledge base articles with name like VPN."
```

## Dry-Run Write Prompts

These are safer for testing because `--dry-run` prevents `POST`, `PATCH`, and `DELETE` requests from being sent to GLPI.

```bash
python -m glpi_agent.cli  "Create a ticket titled 'Printer blocked in accounting' with content 'The accounting printer is blocked and users cannot print invoices.' Priority high."
```

```bash
python -m glpi_agent.cli  "Add a follow-up to ticket 12 saying: The technician checked the switch port and found no physical issue."
```

```bash
python -m glpi_agent.cli  "Set ticket 12 status to pending."
```

```bash
python -m glpi_agent.cli  "Mark ticket 12 as solved."
```

```bash
python -m glpi_agent.cli  "Update ticket 12 title to 'VPN access issue for remote employee'."
```

```bash
python -m glpi_agent.cli  "Add a task to ticket 12: checked the switch port and printer queue, duration 30 minutes."
```

```bash
python -m glpi_agent.cli  "Resolve ticket 12 with solution: replaced toner and printed a test page."
```

```bash
python -m glpi_agent.cli  "Set ticket 12 urgency to 5, impact to 4, and priority to 5."
```

```bash
python -m glpi_agent.cli  "Assign ticket 12 to user ID 2."
```

```bash
python -m glpi_agent.cli  "Assign ticket 12 to group ID 3."
```

```bash
python -m glpi_agent.cli  "Create a printer asset named HP Accounting Printer with serial number ACC-HP-001."
```

```bash
python -m glpi_agent.cli  "Link ticket 12 to printer ID 4."
```

```bash
python -m glpi_agent.cli  "Create a problem titled 'Repeated VPN outages' with content 'Remote users report repeated VPN disconnects every morning.'"
```

```bash
python -m glpi_agent.cli  "Create a change titled 'Upgrade office firewall firmware' with content 'Planned firmware upgrade to address VPN instability.'"
```

```bash
python -m glpi_agent.cli  "Create a knowledge base article titled 'How to reset VPN access' with content 'Steps for first-line support to reset VPN access.'"
```

```bash
python -m glpi_agent.cli  "Delete ticket 12. I confirm deleting ticket 12."
```

```bash
python -m glpi_agent.cli  "Permanently purge ticket 12. I confirm permanently purging ticket 12."
```

## Real Write Prompts

Only run these when you want to change GLPI.

```bash
python -m glpi_agent.cli "Create a low priority ticket titled 'Keyboard replacement request' with content 'User needs a replacement keyboard for workstation HR-04.'"
```

```bash
python -m glpi_agent.cli "Add a follow-up to ticket 12 saying: Waiting for user confirmation after password reset."
```

```bash
python -m glpi_agent.cli "Set ticket 12 status to solved."
```

```bash
python -m glpi_agent.cli "Set ticket 12 status to closed."
```

```bash
python -m glpi_agent.cli "Delete ticket 12. I confirm deleting ticket 12."
```

## Interactive Workflow

Start the agent:

```bash
python -m glpi_agent.cli
```

Then try this sequence:

```text
Show me the 5 newest tickets.
Get ticket 12 with notes.
Add a follow-up to ticket 12 saying the issue is being investigated.
Set ticket 12 status to pending.
```


# Agent 2 — Knowledge Base Agent

## Check Configuration

```bash
python -m glpi_agent.cli_knowledge_base_agent --show-config
```

## Level 1 — KB Answer (local fiches + solved tickets)

These should return a direct solution without creating a ticket:

```bash
python -m glpi_agent.cli_knowledge_base_agent "How do I reset my Windows password?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "I forgot my password and can't log in."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "How do I connect to the VPN?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "Cisco AnyConnect credentials rejected."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "How do I access my emails from home?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "What is the webmail address?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "My printer is not printing."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "Print job stuck in queue."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "How do I request an account for a new employee?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "How do I access SEDIT?"
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "SEDIT shows a blank page."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "I received a suspicious email with an attachment."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "The spacebar on my keyboard is not working."
```

## Level 2 — Ticket Creation (no KB match)

These should create a GLPI ticket immediately:

```bash
python -m glpi_agent.cli_knowledge_base_agent  "My monitor screen is flickering."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent  "My mouse is not working."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent  "The projector in meeting room 3 is broken."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent  "Software crashes when I open large Excel files."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent  "My second monitor is not detected."
```

## Level 3 — Emergency (Help Desk phone)

These should return the support contact number:

```bash
python -m glpi_agent.cli_knowledge_base_agent "URGENT: system is completely down."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "CRITICAL: I can't access payroll and it's due today."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent "EMERGENCY: all my files have disappeared."
```

## With User Email

Passing `--user-email` enables the IT staff rejection check:

```bash
# Non-IT user — proceeds normally
python -m glpi_agent.cli_knowledge_base_agent --user-email "marie.dubois@cd08.fr" "My laptop screen is cracked."
```

```bash
# IT staff email prefix — rejected
python -m glpi_agent.cli_knowledge_base_agent --user-email "tech.admin@cd08.fr" "Reset my password."
```

## With Dry-Run

```bash
python -m glpi_agent.cli_knowledge_base_agent  "My keyboard is broken."
```

```bash
python -m glpi_agent.cli_knowledge_base_agent  "I need a new mouse for my workstation."
```

## Interactive REPL

```bash
python -m glpi_agent.cli_knowledge_base_agent
```

---

## Useful Prompt Patterns

```text
# Agent 1

Search [item type] with name like [text].
Get [item type] [id] and summarize it.
Show the newest [number] [item type].
Create a ticket titled [title] with content [content].
Add a follow-up to ticket [id] saying [message].
Set ticket [id] status to [new, assigned, planned, pending, solved, closed].
Add a task to ticket [id]: [work done], duration [minutes] minutes.
Resolve ticket [id] with solution: [resolution].
Assign ticket [id] to user ID [user_id].
Assign ticket [id] to group ID [group_id].
Create a [Computer/Printer/Software] asset with fields [fields].
Link ticket [id] to [itemtype] ID [item_id].
Create a problem titled [title] with content [content].
Create a change titled [title] with content [content].
Create a knowledge base article titled [title] with content [content].
Delete ticket [id]. I confirm deleting ticket [id].

# Agent 2

How do I [password/vpn/printer/email/sedit/account/security]?
[describe issue] — agent decides: KB answer, ticket, or emergency contact.
URGENT/CRITICAL/EMERGENCY: [describe crisis] — returns Help Desk phone.
```
