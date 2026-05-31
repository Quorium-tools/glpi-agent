from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any

from core.config import Settings
from utils.http_json import request_json


ITEMTYPE_ENDPOINTS = {
    "change": "Assistance/Change",
    "computer": "Assets/Computer",
    "entity": "Administration/Entity",
    "group": "Administration/Group",
    "itilcategory": "Dropdowns/ITILCategory",
    "knowledgebase": "Tools/KnowbaseItem",
    "knowbaseitem": "Tools/KnowbaseItem",
    "location": "Dropdowns/Location",
    "monitor": "Assets/Monitor",
    "networkequipment": "Assets/NetworkEquipment",
    "peripheral": "Assets/Peripheral",
    "phone": "Assets/Phone",
    "printer": "Assets/Printer",
    "problem": "Assistance/Problem",
    "requestsource": "Dropdowns/RequestType",
    "requesttype": "Dropdowns/RequestType",
    "software": "Assets/Software",
    "ticket": "Assistance/Ticket",
    "user": "Administration/User",
}

TICKET_STATUS_CODES = {
    "new": 1,
    "incoming": 1,
    "approval": 10,
    "waiting approval": 10,
    "waiting for approval": 10,
    "pending approval": 10,
    "processing": 2,
    "assigned": 2,
    "processing assigned": 2,
    "processing (assigned)": 2,
    "planned": 3,
    "processing planned": 3,
    "processing (planned)": 3,
    "pending": 4,
    "waiting": 4,
    "solved": 5,
    "resolved": 5,
    "closed": 6,
}

TICKET_TYPE_CODES = {
    "incident": 1,
    "request": 2,
}

TICKET_LEVEL_CODES = {
    "very low": 1,
    "lowest": 1,
    "low": 2,
    "medium": 3,
    "average": 3,
    "high": 4,
    "very high": 5,
    "highest": 6,
    "major": 6,
}


class GlpiClient(AbstractContextManager["GlpiClient"]):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.api_root = f"{settings.GLPI_BASE_URL}/api.php/{settings.glpi_api_version}"
        self.token_url = f"{settings.GLPI_BASE_URL}/api.php/token"
        self.access_token: str | None = None

    def __enter__(self) -> "GlpiClient":
        self.authenticate()
        return self

    def __exit__(self, *args: object) -> None:
        self.access_token = None

    def authenticate(self) -> str:
        result = request_json(
            "POST",
            self.token_url,
            form={
                "grant_type": "password",
                "client_id": self.settings.glpi_oauth_client_id,
                "client_secret": self.settings.glpi_oauth_client_secret,
                "username": self.settings.glpi_username,
                "password": self.settings.glpi_password,
                "scope": self.settings.glpi_oauth_scope,
            },
        )
        self.access_token = result["access_token"]
        return self.access_token

    def get_item(self, itemtype: str, item_id: int, **query: Any) -> Any:
        return request_json(
            "GET",
            f"{self.api_root}/{self._endpoint(itemtype)}/{item_id}",
            headers=self._auth_headers(),
            query=self._clean_query(
                query,
                allowed={
                    "expand_dropdowns",
                    "with_tickets",
                    "with_notes",
                    "with_logs",
                    "with_documents",
                    "with_infocoms",
                    "sort",
                },
            ),
        )

    def list_items(self, itemtype: str, range_: str = "0-19", **query: Any) -> Any:
        start, limit = self._range_to_pagination(range_)
        return request_json(
            "GET",
            f"{self.api_root}/{self._endpoint(itemtype)}",
            headers=self._auth_headers(),
            query=self._clean_query({"start": start, "limit": limit, **query}, allowed={"start", "limit", "filter", "sort"}),
        )

    def list_all_items(
        self,
        itemtype: str,
        max_items: int = 100,
        page_size: int = 50,
        filter: str | None = None,
        sort: str | None = None,
    ) -> list[Any]:
        max_items = min(max(max_items, 1), 500)
        page_size = min(max(page_size, 1), 100)
        items: list[Any] = []

        while len(items) < max_items:
            start = len(items)
            limit = min(page_size, max_items - start)
            page = self.list_items(
                itemtype,
                range_=f"{start}-{start + limit - 1}",
                filter=filter,
                sort=sort,
            )
            if not isinstance(page, list) or not page:
                break
            items.extend(page)
            if len(page) < limit:
                break

        return items

    def search_items(
        self,
        itemtype: str,
        filter: str | None = None,
        start: int = 0,
        limit: int = 20,
        sort: str | None = None,
    ) -> Any:
        return self.list_items(itemtype, range_=f"{start}-{start + limit - 1}", filter=filter, sort=sort)

    def create_item(self, itemtype: str, fields: dict[str, Any]) -> Any:
        return self._write("POST", f"{self.api_root}/{self._endpoint(itemtype)}", fields)

    def update_item(self, itemtype: str, item_id: int, fields: dict[str, Any]) -> Any:
        return self._write("PATCH", f"{self.api_root}/{self._endpoint(itemtype)}/{item_id}", fields)

    def delete_item(self, itemtype: str, item_id: int, force_purge: bool = False) -> Any:
        return self._write(
            "DELETE",
            f"{self.api_root}/{self._endpoint(itemtype)}/{item_id}",
            {"force": force_purge},
        )

    def create_ticket(
        self,
        title: str,
        content: str,
        priority: int | str | None = None,
        opening_date: str | None = None,
        type: int | str | None = None,
        category_id: int | None = None,
        request_source_id: int | None = None,
        urgency: int | str | None = None,
        impact: int | str | None = None,
        total_duration_minutes: int | None = None,
        external_id: str | None = None,
        requester_user_id: int | None = None,
        observer_user_id: int | None = None,
        assigned_user_id: int | None = None,
        requester_group_id: int | None = None,
        observer_group_id: int | None = None,
        assigned_group_id: int | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload = self._build_ticket_payload(
            title=title,
            content=content,
            priority=priority,
            opening_date=opening_date,
            type=type,
            category_id=category_id,
            request_source_id=request_source_id,
            urgency=urgency,
            impact=impact,
            total_duration_minutes=total_duration_minutes,
            external_id=external_id,
            requester_user_id=requester_user_id,
            observer_user_id=observer_user_id,
            assigned_user_id=assigned_user_id,
            requester_group_id=requester_group_id,
            observer_group_id=observer_group_id,
            assigned_group_id=assigned_group_id,
            fields=fields,
        )
        return self.create_item("Ticket", payload)

    def list_tickets(
        self,
        max_items: int = 50,
        page_size: int = 50,
        filter: str | None = None,
        sort: str | None = None,
        include_deleted: bool = False,
    ) -> dict[str, Any]:
        tickets = self.list_all_items("Ticket", max_items=max_items, page_size=page_size, filter=filter, sort=sort)
        if not include_deleted:
            tickets = [ticket for ticket in tickets if not (isinstance(ticket, dict) and ticket.get("is_deleted"))]
        return {
            "total_returned": len(tickets),
            "tickets": [self._ticket_summary(ticket) for ticket in tickets if isinstance(ticket, dict)],
            "format_instruction": (
                "Answer with a short compact list. Deleted tickets are hidden unless include_deleted=true. "
                "Use each ticket priority_code and priority_label exactly as returned; do not remap or reinterpret them."
            ),
        }

    def get_ticket(
        self,
        ticket_id: int,
        expand_dropdowns: bool = True,
        with_tickets: bool = False,
        with_notes: bool = True,
        with_logs: bool = False,
        with_documents: bool = False,
    ) -> Any:
        return self.get_item(
            "Ticket",
            ticket_id,
            expand_dropdowns=expand_dropdowns,
            with_tickets=with_tickets,
            with_notes=with_notes,
            with_logs=with_logs,
            with_documents=with_documents,
        )

    def create_problem(self, title: str, content: str, priority: int | None = None) -> Any:
        fields: dict[str, Any] = {"name": title, "content": content}
        if priority is not None:
            fields["priority"] = priority
        return self.create_item("Problem", fields)

    def create_change(self, title: str, content: str, priority: int | None = None) -> Any:
        fields: dict[str, Any] = {"name": title, "content": content}
        if priority is not None:
            fields["priority"] = priority
        return self.create_item("Change", fields)

    def create_asset(self, itemtype: str, fields: dict[str, Any]) -> Any:
        if itemtype.replace("_", "").replace("-", "").lower() not in {
            "computer",
            "monitor",
            "networkequipment",
            "peripheral",
            "phone",
            "printer",
            "software",
        } and "/" not in itemtype:
            raise ValueError("create_asset only supports asset item types such as Computer, Printer, Software, or a full API path.")
        return self.create_item(itemtype, fields)

    def create_knowledge_base_item(self, title: str, content: str, fields: dict[str, Any] | None = None) -> Any:
        payload = {"name": title, "content": content, **(fields or {})}
        return self.create_item("KnowledgeBase", payload)

    def update_ticket_fields(
        self,
        ticket_id: int,
        urgency: int | str | None = None,
        impact: int | str | None = None,
        priority: int | str | None = None,
        category_id: int | None = None,
        location_id: int | None = None,
        request_source_id: int | None = None,
        total_duration_minutes: int | None = None,
        external_id: str | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload = dict(fields or {})
        for key, value in {
            "urgency": self._ticket_level_code(urgency) if urgency is not None else None,
            "impact": self._ticket_level_code(impact) if impact is not None else None,
            "priority": self._ticket_level_code(priority) if priority is not None else None,
            "category": category_id,
            "location": location_id,
            "request_type": request_source_id,
            "actiontime": max(total_duration_minutes, 0) * 60 if total_duration_minutes is not None else None,
            "external_id": external_id,
        }.items():
            if value is not None:
                payload[key] = value
        if not payload:
            raise ValueError("No ticket fields were provided.")
        return self.update_item("Ticket", ticket_id, payload)

    def update_ticket(
        self,
        ticket_id: int,
        title: str | None = None,
        content: str | None = None,
        status: int | str | None = None,
        priority: int | str | None = None,
        urgency: int | str | None = None,
        impact: int | str | None = None,
        opening_date: str | None = None,
        type: int | str | None = None,
        category_id: int | None = None,
        location_id: int | None = None,
        request_source_id: int | None = None,
        total_duration_minutes: int | None = None,
        external_id: str | None = None,
        requester_user_id: int | None = None,
        observer_user_id: int | None = None,
        assigned_user_id: int | None = None,
        requester_group_id: int | None = None,
        observer_group_id: int | None = None,
        assigned_group_id: int | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload = self._build_ticket_payload(
            title=title,
            content=content,
            status=status,
            priority=priority,
            urgency=urgency,
            impact=impact,
            opening_date=opening_date,
            type=type,
            category_id=category_id,
            location_id=location_id,
            request_source_id=request_source_id,
            total_duration_minutes=total_duration_minutes,
            external_id=external_id,
            requester_user_id=requester_user_id,
            observer_user_id=observer_user_id,
            assigned_user_id=assigned_user_id,
            requester_group_id=requester_group_id,
            observer_group_id=observer_group_id,
            assigned_group_id=assigned_group_id,
            fields=fields,
        )
        if not payload:
            raise ValueError("No ticket fields were provided.")
        return self.update_item("Ticket", ticket_id, payload)

    def update_ticket_status(self, ticket_id: int, status: int | str) -> Any:
        return self.update_item("Ticket", ticket_id, {"status": self._ticket_status_code(status)})

    def assign_ticket_user(self, ticket_id: int, user_id: int) -> Any:
        return self.update_item("Ticket", ticket_id, {"user_assigned": user_id})

    def assign_ticket_group(self, ticket_id: int, group_id: int) -> Any:
        return self.update_item("Ticket", ticket_id, {"group_assigned": group_id})

    def update_ticket_actors(
        self,
        ticket_id: int,
        requester_user_id: int | None = None,
        observer_user_id: int | None = None,
        assigned_user_id: int | None = None,
        requester_group_id: int | None = None,
        observer_group_id: int | None = None,
        assigned_group_id: int | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload = self._build_ticket_payload(
            requester_user_id=requester_user_id,
            observer_user_id=observer_user_id,
            assigned_user_id=assigned_user_id,
            requester_group_id=requester_group_id,
            observer_group_id=observer_group_id,
            assigned_group_id=assigned_group_id,
            fields=fields,
        )
        if not payload:
            raise ValueError("No ticket actors were provided.")
        return self.update_item("Ticket", ticket_id, payload)

    def delete_ticket(self, ticket_id: int, force_purge: bool = False, confirm: bool = False) -> Any:
        if not confirm:
            return {
                "error": "Deletion requires explicit confirmation.",
                "required_confirmation": f"Delete ticket {ticket_id} with confirm=true",
                "ticket_id": ticket_id,
                "force_purge": force_purge,
            }
        return self.delete_item("Ticket", ticket_id, force_purge=force_purge)

    def add_ticket_followup(self, ticket_id: int, content: str) -> Any:
        return self._write(
            "POST",
            f"{self.api_root}/Assistance/Ticket/{ticket_id}/Timeline/Followup",
            {"content": content},
        )

    def add_ticket_task(
        self,
        ticket_id: int,
        content: str,
        duration_minutes: int | None = None,
        user_id: int | None = None,
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {"content": content, **(fields or {})}
        if duration_minutes is not None:
            payload["actiontime"] = max(duration_minutes, 0) * 60
        if user_id is not None:
            payload["user_tech"] = user_id
        return self._write("POST", f"{self.api_root}/Assistance/Ticket/{ticket_id}/Timeline/Task", payload)

    def add_ticket_solution(
        self,
        ticket_id: int,
        content: str,
        status: str | int | None = "solved",
        fields: dict[str, Any] | None = None,
    ) -> Any:
        payload = {"content": content, **(fields or {})}
        result = self._write("POST", f"{self.api_root}/Assistance/Ticket/{ticket_id}/Timeline/Solution", payload)
        if status is None:
            return result
        return {"solution": result, "status_update": self.update_ticket_status(ticket_id, status)}

    def get_ticket_solution_context(self, ticket_id: int) -> Any:
        ticket = self.get_ticket(ticket_id, expand_dropdowns=True, with_notes=True, with_logs=True, with_documents=True)
        return {
            "ticket": ticket,
            "instruction": (
                "Use this ticket context to suggest a practical support response. "
                "Do not write a solution unless the user explicitly asks to add it."
            ),
        }

    def link_ticket_item(self, ticket_id: int, itemtype: str, item_id: int, fields: dict[str, Any] | None = None) -> Any:
        payload = {"itemtype": itemtype, "items_id": item_id, **(fields or {})}
        return self._write("POST", f"{self.api_root}/Assistance/Ticket/{ticket_id}/Item", payload)

    def ticket_report(self, max_items: int = 200, filter: str | None = None) -> dict[str, Any]:
        tickets = self.list_all_items("Ticket", max_items=max_items, filter=filter)
        return {
            "total": len(tickets),
            "by_status": self._count_nested_name(tickets, "status"),
            "by_priority": self._count_scalar(tickets, "priority"),
            "by_urgency": self._count_scalar(tickets, "urgency"),
            "by_impact": self._count_scalar(tickets, "impact"),
            "oldest_open": self._oldest_open_tickets(tickets),
        }

    def _write(self, method: str, url: str, payload: dict[str, Any]) -> Any:
        if self.settings.dry_run:
            return {"dry_run": True, "method": method, "url": url, "payload": payload}
        return request_json(method, url, headers=self._auth_headers(), payload=payload)

    def _auth_headers(self) -> dict[str, str]:
        if not self.access_token:
            raise RuntimeError("GLPI OAuth access token is not initialized.")
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def _endpoint(self, itemtype: str) -> str:
        normalized = itemtype.replace("_", "").replace("-", "").lower()
        endpoint = ITEMTYPE_ENDPOINTS.get(normalized)
        if endpoint:
            return endpoint
        if "/" in itemtype:
            return itemtype.strip("/")
        raise ValueError(
            f"Unsupported GLPI V2 item type '{itemtype}'. Use a full API path like "
            "'Assets/Computer' or add it to ITEMTYPE_ENDPOINTS."
        )

    @staticmethod
    def _ticket_status_code(status: int | str) -> int:
        if isinstance(status, int):
            if 1 <= status <= 6:
                return status
            raise ValueError("Ticket status code must be between 1 and 6.")

        normalized = status.strip().lower().replace("-", " ").replace("_", " ")
        normalized = " ".join(normalized.split())
        if normalized in TICKET_STATUS_CODES:
            return TICKET_STATUS_CODES[normalized]
        raise ValueError(
            "Unsupported ticket status. Use one of: new, approval, processing assigned, "
            "processing planned, pending, solved, closed, or a GLPI status code."
        )

    @staticmethod
    def _ticket_type_code(type_: int | str) -> int:
        if isinstance(type_, int):
            if type_ in {1, 2}:
                return type_
            raise ValueError("Ticket type code must be 1 for incident or 2 for request.")

        normalized = type_.strip().lower().replace("-", " ").replace("_", " ")
        normalized = " ".join(normalized.split())
        if normalized in TICKET_TYPE_CODES:
            return TICKET_TYPE_CODES[normalized]
        raise ValueError("Unsupported ticket type. Use incident, request, 1, or 2.")

    @staticmethod
    def _ticket_level_code(level: int | str) -> int:
        if isinstance(level, int):
            if 1 <= level <= 6:
                return level
            raise ValueError("Ticket urgency, impact, and priority must be between 1 and 6.")

        normalized = level.strip().lower().replace("-", " ").replace("_", " ")
        normalized = " ".join(normalized.split())
        if normalized in TICKET_LEVEL_CODES:
            return TICKET_LEVEL_CODES[normalized]
        if normalized.isdigit():
            return GlpiClient._ticket_level_code(int(normalized))
        raise ValueError("Unsupported level. Use very low, low, medium, high, very high, major, or a code from 1 to 6.")

    @staticmethod
    def _count_scalar(items: list[Any], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = item.get(key) if isinstance(item, dict) else None
            label = str(value if value is not None else "empty")
            counts[label] = counts.get(label, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _count_nested_name(items: list[Any], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = item.get(key) if isinstance(item, dict) else None
            if isinstance(value, dict):
                label = str(value.get("name") or value.get("id") or "empty")
            else:
                label = str(value if value is not None else "empty")
            counts[label] = counts.get(label, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _oldest_open_tickets(tickets: list[Any], limit: int = 10) -> list[dict[str, Any]]:
        open_tickets = []
        for ticket in tickets:
            if not isinstance(ticket, dict):
                continue
            status = ticket.get("status")
            status_name = status.get("name") if isinstance(status, dict) else str(status or "")
            if status_name.lower() in {"closed", "solved", "resolved"}:
                continue
            open_tickets.append(
                {
                    "id": ticket.get("id"),
                    "name": ticket.get("name"),
                    "status": status_name,
                    "priority": ticket.get("priority"),
                    "date_creation": ticket.get("date_creation") or ticket.get("date"),
                }
            )
        return sorted(open_tickets, key=lambda item: str(item.get("date_creation") or ""))[:limit]

    @staticmethod
    def _ticket_summary(ticket: dict[str, Any]) -> dict[str, Any]:
        status = ticket.get("status")
        if isinstance(status, dict):
            status_label = status.get("name") or status.get("id")
        else:
            status_label = status
        priority_code, priority_label = GlpiClient._priority_fields(ticket.get("priority"))
        return {
            "id": ticket.get("id"),
            "title": ticket.get("name"),
            "status": status_label,
            "priority": ticket.get("priority"),
            "priority_code": priority_code,
            "priority_label": priority_label,
            "date": ticket.get("date") or ticket.get("date_creation"),
        }

    @staticmethod
    def _priority_fields(priority: Any) -> tuple[int | None, str]:
        if isinstance(priority, int):
            return priority, f"P{priority}"
        if isinstance(priority, str):
            text = priority.strip()
            if text.isdigit():
                value = int(text)
                return value, f"P{value}"
            return None, text or "unknown"
        if isinstance(priority, dict):
            code = priority.get("id") if isinstance(priority.get("id"), int) else None
            label = str(priority.get("name") or "").strip()
            if code is None and isinstance(priority.get("id"), str) and str(priority.get("id")).isdigit():
                code = int(str(priority.get("id")))
            if not label and code is not None:
                label = f"P{code}"
            return code, label or "unknown"
        return None, "unknown"

    @classmethod
    def _build_ticket_payload(
        cls,
        title: str | None = None,
        content: str | None = None,
        status: int | str | None = None,
        priority: int | str | None = None,
        urgency: int | str | None = None,
        impact: int | str | None = None,
        opening_date: str | None = None,
        type: int | str | None = None,
        category_id: int | None = None,
        location_id: int | None = None,
        request_source_id: int | None = None,
        total_duration_minutes: int | None = None,
        external_id: str | None = None,
        requester_user_id: int | None = None,
        observer_user_id: int | None = None,
        assigned_user_id: int | None = None,
        requester_group_id: int | None = None,
        observer_group_id: int | None = None,
        assigned_group_id: int | None = None,
        fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(fields or {})
        for key, value in {
            "name": title,
            "content": content,
            "date": opening_date,
            "type": cls._ticket_type_code(type) if type is not None else None,
            "category": category_id,
            "location": location_id,
            "status": cls._ticket_status_code(status) if status is not None else None,
            "request_type": request_source_id,
            "urgency": cls._ticket_level_code(urgency) if urgency is not None else None,
            "impact": cls._ticket_level_code(impact) if impact is not None else None,
            "priority": cls._ticket_level_code(priority) if priority is not None else None,
            "actiontime": max(total_duration_minutes, 0) * 60 if total_duration_minutes is not None else None,
            "external_id": external_id,
            "user_requester": requester_user_id,
            "user_observer": observer_user_id,
            "user_assigned": assigned_user_id,
            "group_requester": requester_group_id,
            "group_observer": observer_group_id,
            "group_assigned": assigned_group_id,
        }.items():
            if value is not None:
                payload[key] = value
        return payload

    @staticmethod
    def _range_to_pagination(range_: str) -> tuple[int, int]:
        try:
            start_text, end_text = range_.split("-", 1)
            start = int(start_text)
            end = int(end_text)
        except ValueError:
            return 0, 20
        return start, max(end - start + 1, 1)

    @staticmethod
    def _clean_query(
        query: dict[str, Any],
        allowed: set[str] | None = None,
    ) -> dict[str, Any]:
        allowed = allowed or {"filter", "start", "limit", "sort"}
        return {key: value for key, value in query.items() if key in allowed and value is not None}
