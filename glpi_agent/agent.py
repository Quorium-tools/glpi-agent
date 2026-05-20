from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Callable

from .glpi_client import ITEMTYPE_ENDPOINTS, TICKET_STATUS_CODES, GlpiClient
from .openrouter_client import OpenRouterClient


SYSTEM_PROMPT = """You are a GLPI operations agent.
Use tools for GLPI data or changes. Do not invent ticket IDs or statuses.
For read requests, fetch data before answering.
For create/update/follow-up operations, keep payloads concise and professional and summarize what changed.
For ticket status changes, prefer the update_ticket_status tool instead of raw update_item fields.
For ticket deletion, never delete from a vague request. If the user has not clearly confirmed the exact ticket ID, ask for confirmation first. Only call delete_ticket with confirm=true when the user explicitly confirms deletion of that exact ticket.
For assignment and asset linking, search users/groups/assets first when the user gives a name instead of an ID.
If a tool result contains dry_run=true, explain that this was only a preview and no GLPI data was changed. Do not describe dry-run as a failure.
When a GLPI API call fails, explain the exact error and suggest the next fix.
If the user asks what you can do, explain the available tools without calling GLPI.
"""


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_supported_itemtypes",
            "description": "List the friendly GLPI item type names this agent can map to API V2 paths.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_items",
            "description": "List one page of GLPI items by item type, for example Ticket, Computer, User.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "range": {"type": "string", "default": "0-19"},
                },
                "required": ["itemtype"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_items",
            "description": "List all available GLPI items up to a safe maximum. Use this when the user asks for all tickets or all items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "max_items": {"type": "integer", "default": 100, "minimum": 1, "maximum": 500},
                    "page_size": {"type": "integer", "default": 50, "minimum": 1, "maximum": 100},
                    "filter": {"type": "string"},
                    "sort": {"type": "string"},
                },
                "required": ["itemtype"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_item",
            "description": "Get one GLPI item by item type and ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "item_id": {"type": "integer"},
                    "expand_dropdowns": {"type": "boolean", "default": True},
                    "with_tickets": {"type": "boolean", "default": False},
                    "with_notes": {"type": "boolean", "default": False},
                },
                "required": ["itemtype", "item_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_items",
            "description": "Search GLPI items using a V2 RSQL filter, for example name=ilike=laptop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "filter": {"type": "string"},
                    "start": {"type": "integer", "default": 0},
                    "limit": {"type": "integer", "default": 20},
                    "sort": {"type": "string"},
                },
                "required": ["itemtype"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a GLPI ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 6},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_problem",
            "description": "Create a GLPI problem record for recurring or root-cause incidents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 6},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_change",
            "description": "Create a GLPI change record for planned infrastructure or service changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 6},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_asset",
            "description": "Create an asset such as Computer, Printer, Monitor, Phone, NetworkEquipment, Peripheral, or Software.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "fields": {"type": "object"},
                },
                "required": ["itemtype", "fields"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_knowledge_base_item",
            "description": "Create a GLPI knowledge base item/article.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "fields": {"type": "object"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_item",
            "description": "Update a GLPI item by item type and ID. Use update_ticket_status for ticket status changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itemtype": {"type": "string"},
                    "item_id": {"type": "integer"},
                    "fields": {"type": "object"},
                },
                "required": ["itemtype", "item_id", "fields"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_ticket_fields",
            "description": "Update common ticket fields such as urgency, impact, priority, category, location, plus optional raw fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "urgency": {"type": "integer", "minimum": 1, "maximum": 6},
                    "impact": {"type": "integer", "minimum": 1, "maximum": 6},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 6},
                    "category_id": {"type": "integer"},
                    "location_id": {"type": "integer"},
                    "fields": {"type": "object"},
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_ticket_status",
            "description": "Update a ticket status using a readable name like solved, pending, closed, or a GLPI status code 1-6.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "status": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "integer", "minimum": 1, "maximum": 6},
                        ]
                    },
                },
                "required": ["ticket_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assign_ticket_user",
            "description": "Assign a ticket to a technician/user by user ID. Search User first when only a name is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                },
                "required": ["ticket_id", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assign_ticket_group",
            "description": "Assign a ticket to a group by group ID. Search Group first when only a name is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "group_id": {"type": "integer"},
                },
                "required": ["ticket_id", "group_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_ticket_followup",
            "description": "Add a follow-up/comment to a GLPI ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "content": {"type": "string"},
                },
                "required": ["ticket_id", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_ticket_task",
            "description": "Add a technical task/worklog to a ticket, optionally with duration and assigned technician ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "content": {"type": "string"},
                    "duration_minutes": {"type": "integer", "minimum": 0},
                    "user_id": {"type": "integer"},
                    "fields": {"type": "object"},
                },
                "required": ["ticket_id", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_ticket_solution",
            "description": "Add a solution/resolution to a ticket and optionally update the ticket status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "content": {"type": "string"},
                    "status": {
                        "anyOf": [
                            {"type": "string"},
                            {"type": "integer", "minimum": 1, "maximum": 6},
                            {"type": "null"}
                        ],
                        "default": "solved"
                    },
                    "fields": {"type": "object"},
                },
                "required": ["ticket_id", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "link_ticket_item",
            "description": "Link an asset or other GLPI item to a ticket. Search the item first when only a name is provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "itemtype": {"type": "string"},
                    "item_id": {"type": "integer"},
                    "fields": {"type": "object"},
                },
                "required": ["ticket_id", "itemtype", "item_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_ticket",
            "description": "Delete a GLPI ticket by ID. Requires explicit confirmation for the exact ticket ID. Set force_purge=true only when the user explicitly asks for permanent purge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "integer"},
                    "force_purge": {"type": "boolean", "default": False},
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be true only after the user explicitly confirms deletion of this exact ticket ID.",
                    },
                },
                "required": ["ticket_id", "confirm"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ticket_report",
            "description": "Build a simple ticket summary report with counts by status, priority, urgency, impact, and oldest open tickets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_items": {"type": "integer", "default": 200, "minimum": 1, "maximum": 500},
                    "filter": {"type": "string"},
                },
            },
        },
    },
]


class GlpiAgent:
    def __init__(self, llm: OpenRouterClient, glpi: GlpiClient) -> None:
        self.llm = llm
        self.glpi = glpi
        self.tool_handlers: dict[str, Callable[..., Any]] = {
            "list_supported_itemtypes": self._list_supported_itemtypes,
            "list_items": self._list_items,
            "list_all_items": self.glpi.list_all_items,
            "get_item": self.glpi.get_item,
            "search_items": self.glpi.search_items,
            "create_ticket": self.glpi.create_ticket,
            "create_problem": self.glpi.create_problem,
            "create_change": self.glpi.create_change,
            "create_asset": self.glpi.create_asset,
            "create_knowledge_base_item": self.glpi.create_knowledge_base_item,
            "update_item": self.glpi.update_item,
            "update_ticket_fields": self.glpi.update_ticket_fields,
            "update_ticket_status": self.glpi.update_ticket_status,
            "assign_ticket_user": self.glpi.assign_ticket_user,
            "assign_ticket_group": self.glpi.assign_ticket_group,
            "add_ticket_followup": self.glpi.add_ticket_followup,
            "add_ticket_task": self.glpi.add_ticket_task,
            "add_ticket_solution": self.glpi.add_ticket_solution,
            "link_ticket_item": self.glpi.link_ticket_item,
            "delete_ticket": self.glpi.delete_ticket,
            "ticket_report": self.glpi.ticket_report,
        }

    def run(self, user_message: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        for _ in range(6):
            response = self.llm.chat(messages, TOOLS)
            assistant_message = self._assistant_message(response)
            messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls") or []
            if not tool_calls:
                return assistant_message.get("content") or ""

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                arguments = self._tool_arguments(tool_call)
                result = self._call_tool(name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": name,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        return "The agent reached the tool-call limit before completing the request."

    @staticmethod
    def _assistant_message(response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError(f"OpenRouter returned no choices: {response}")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"OpenRouter returned an invalid message: {response}")
        return message

    @staticmethod
    def _tool_arguments(tool_call: dict[str, Any]) -> dict[str, Any]:
        raw_arguments = tool_call.get("function", {}).get("arguments") or "{}"
        try:
            arguments = json.loads(raw_arguments)
        except JSONDecodeError as exc:
            return {"_argument_error": f"Tool arguments were not valid JSON: {exc}", "_raw": raw_arguments}
        if not isinstance(arguments, dict):
            return {"_argument_error": "Tool arguments must be a JSON object.", "_raw": raw_arguments}
        return arguments

    def _call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if "_argument_error" in arguments:
            return {"error": arguments["_argument_error"], "raw_arguments": arguments.get("_raw")}

        handler = self.tool_handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        try:
            return handler(**arguments)
        except Exception as exc:
            return {"error": str(exc), "tool": name, "arguments": arguments}

    def _list_supported_itemtypes(self) -> dict[str, Any]:
        return {
            "itemtypes": dict(sorted(ITEMTYPE_ENDPOINTS.items())),
            "ticket_statuses": dict(sorted(TICKET_STATUS_CODES.items())),
            "note": "You can also use a full GLPI V2 path like Assets/Computer or Assistance/Ticket.",
        }

    def _list_items(
        self,
        itemtype: str,
        range: str = "0-19",
    ) -> Any:
        return self.glpi.list_items(itemtype, range_=range)
