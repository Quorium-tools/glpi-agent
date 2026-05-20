# GLPI Agent Examples

Use these after your `.env` is configured.

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
python -m glpi_agent.cli --dry-run "Update ticket 12 title to 'VPN access issue for remote employee'."
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

```bash
python -m glpi_agent.cli --dry-run "Delete ticket 12. I confirm deleting ticket 12."
```

```bash
python -m glpi_agent.cli --dry-run "Permanently purge ticket 12. I confirm permanently purging ticket 12."
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

## Useful Prompt Patterns

```text
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
```
