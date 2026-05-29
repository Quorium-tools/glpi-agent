# GLPI Agent Examples

Use these after your `.env` is configured.

# Agent 1 — IT Admin Agent

## Check Configuration

```bash
python -m help_desk_agent.cli --show-config
```

Try another OpenRouter model for one run:

```bash
python -m help_desk_agent.cli --model anthropic/claude-3.5-sonnet "Show me the 5 newest tickets"
```

## Safe Read-Only Prompts

```bash
python -m help_desk_agent.cli "What can you do with GLPI?"
```

```bash
python -m help_desk_agent.cli "List the supported GLPI item types."
```

```bash
python -m help_desk_agent.cli "Show me the 10 newest tickets with their ID, title, status, and priority."
```

```bash
python -m help_desk_agent.cli "List all tickets I have."
```

```bash
python -m help_desk_agent.cli "Get ticket 12 and summarize the issue, requester, status, and latest notes if available."
```

```bash
python -m help_desk_agent.cli "Search computers with name like laptop and show ID, name, serial number, and entity."
```

```bash
python -m help_desk_agent.cli "List 10 printers and show their ID, name, location, and status."
```

```bash
python -m help_desk_agent.cli "Find users with name like souhail and show the closest matches."
```

```bash
python -m help_desk_agent.cli "List recent problems and summarize them as a table."
```

```bash
python -m help_desk_agent.cli "Generate a ticket report grouped by status, priority, urgency, and impact."
```

```bash
python -m help_desk_agent.cli "Search groups with name like support."
```

```bash
python -m help_desk_agent.cli "Search knowledge base articles with name like VPN."
```

## Dry-Run Write Prompts

These are safer for testing because `--dry-run` prevents `POST`, `PATCH`, and `DELETE` requests from being sent to GLPI.

```bash
python -m help_desk_agent.cli  "Create a ticket titled 'Printer blocked in accounting' with content 'The accounting printer is blocked and users cannot print invoices.' Priority high."
```

```bash
python -m help_desk_agent.cli  "Add a follow-up to ticket 12 saying: The technician checked the switch port and found no physical issue."
```

```bash
python -m help_desk_agent.cli  "Set ticket 12 status to pending."
```

```bash
python -m help_desk_agent.cli  "Mark ticket 12 as solved."
```

```bash
python -m help_desk_agent.cli  "Update ticket 12 title to 'VPN access issue for remote employee'."
```

```bash
python -m help_desk_agent.cli  "Add a task to ticket 12: checked the switch port and printer queue, duration 30 minutes."
```

```bash
python -m help_desk_agent.cli  "Resolve ticket 12 with solution: replaced toner and printed a test page."
```

```bash
python -m help_desk_agent.cli  "Set ticket 12 urgency to 5, impact to 4, and priority to 5."
```

```bash
python -m help_desk_agent.cli  "Assign ticket 12 to user ID 2."
```

```bash
python -m help_desk_agent.cli  "Assign ticket 12 to group ID 3."
```

```bash
python -m help_desk_agent.cli  "Create a printer asset named HP Accounting Printer with serial number ACC-HP-001."
```

```bash
python -m help_desk_agent.cli  "Link ticket 12 to printer ID 4."
```

```bash
python -m help_desk_agent.cli  "Create a problem titled 'Repeated VPN outages' with content 'Remote users report repeated VPN disconnects every morning.'"
```

```bash
python -m help_desk_agent.cli  "Create a change titled 'Upgrade office firewall firmware' with content 'Planned firmware upgrade to address VPN instability.'"
```

```bash
python -m help_desk_agent.cli  "Create a knowledge base article titled 'How to reset VPN access' with content 'Steps for first-line support to reset VPN access.'"
```

```bash
python -m help_desk_agent.cli  "Delete ticket 12. I confirm deleting ticket 12."
```

```bash
python -m help_desk_agent.cli  "Permanently purge ticket 12. I confirm permanently purging ticket 12."
```

## Real Write Prompts

Only run these when you want to change GLPI.

```bash
python -m help_desk_agent.cli "Create a low priority ticket titled 'Keyboard replacement request' with content 'User needs a replacement keyboard for workstation HR-04.'"
```

```bash
python -m help_desk_agent.cli "Add a follow-up to ticket 12 saying: Waiting for user confirmation after password reset."
```

```bash
python -m help_desk_agent.cli "Set ticket 12 status to solved."
```

```bash
python -m help_desk_agent.cli "Set ticket 12 status to closed."
```

```bash
python -m help_desk_agent.cli "Delete ticket 12. I confirm deleting ticket 12."
```

## Interactive Workflow

Start the agent:

```bash
python -m help_desk_agent.cli
```

Then try this sequence:

```text
Show me the 5 newest tickets.
Get ticket 12 with notes.
Add a follow-up to ticket 12 saying the issue is being investigated.
Set ticket 12 status to pending.
```


# Agent 2 — Departments Support Agent

## Check Configuration

```bash
python -m departments_support_agent.cli --show-config
```

## Level 1 — KB Answer (local fiches + solved tickets)

These should return a direct solution without creating a ticket:

```bash
python -m departments_support_agent.cli "How do I reset my Windows password?"
```

```bash
python -m departments_support_agent.cli "I forgot my password and can't log in."
```

```bash
python -m departments_support_agent.cli "How do I connect to the VPN?"
```

```bash
python -m departments_support_agent.cli "Cisco AnyConnect credentials rejected."
```

```bash
python -m departments_support_agent.cli "How do I access my emails from home?"
```

```bash
python -m departments_support_agent.cli "What is the webmail address?"
```

```bash
python -m departments_support_agent.cli "My printer is not printing."
```

```bash
python -m departments_support_agent.cli "Print job stuck in queue."
```

```bash
python -m departments_support_agent.cli "How do I request an account for a new employee?"
```

```bash
python -m departments_support_agent.cli "How do I access SEDIT?"
```

```bash
python -m departments_support_agent.cli "SEDIT shows a blank page."
```

```bash
python -m departments_support_agent.cli "I received a suspicious email with an attachment."
```

```bash
python -m departments_support_agent.cli "The spacebar on my keyboard is not working."
```

## Level 2 — Ticket Creation (no KB match)

These should create a GLPI ticket immediately:

```bash
python -m departments_support_agent.cli  "My monitor screen is flickering."
```

```bash
python -m departments_support_agent.cli  "My mouse is not working."
```

```bash
python -m departments_support_agent.cli  "The projector in meeting room 3 is broken."
```

```bash
python -m departments_support_agent.cli  "Software crashes when I open large Excel files."
```

```bash
python -m departments_support_agent.cli  "My second monitor is not detected."
```

## Level 3 — Emergency (Help Desk phone)

These should return the support contact number:

```bash
python -m departments_support_agent.cli "URGENT: system is completely down."
```

```bash
python -m departments_support_agent.cli "CRITICAL: I can't access payroll and it's due today."
```

```bash
python -m departments_support_agent.cli "EMERGENCY: all my files have disappeared."
```

## With User Email

Passing `--user-email` enables the IT staff rejection check:

```bash
# Non-IT user — proceeds normally
python -m departments_support_agent.cli --user-email "marie.dubois@cd08.fr" "My laptop screen is cracked."
```

```bash
# IT staff email prefix — rejected
python -m departments_support_agent.cli --user-email "tech.admin@cd08.fr" "Reset my password."
```

## With Dry-Run

```bash
python -m departments_support_agent.cli  "My keyboard is broken."
```

```bash
python -m departments_support_agent.cli  "I need a new mouse for my workstation."
```

## Interactive REPL

```bash
python -m departments_support_agent.cli
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
