from __future__ import annotations

import json
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Callable

from clients.glpi_client import GlpiClient
from clients.openrouter_client import OpenRouterClient
from utils.http_json import request_json


_GENERIC_WORDS = {
    "working", "broken", "issue", "problem", "help", "need", "with", "that",
    "this", "have", "cannot", "cant", "dont", "does", "work", "fail", "error",
    "able", "please", "when", "what", "where", "getting", "keeps",
}

_CREATE_CONFIRM_KEYWORDS = {
    "confirmer",
    "crée",
    "créer le ticket",
    "créer un ticket",
    "crée le ticket",
    "oui",
    "yes",
    "yes create it",
    "create it",
    "create ticket",
    "open ticket",
    "ok create",
    "please create",
}

_DECLINE_KEYWORDS = {"no", "n", "non", "non merci", "pas maintenant", "don't create", "do not create"}

_TICKET_FORM_PREFIX = "__TICKET_FORM__"

# ── Local knowledge base (loaded from knowledge/*.md) ────────────────────────

_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
_TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9_-]{2,}")


def _load_folder_kb() -> list[dict[str, Any]]:
    if not _KNOWLEDGE_DIR.exists():
        return []

    entries: list[dict[str, Any]] = []
    for file_path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        raw = file_path.read_text(encoding="utf-8").strip()
        if not raw:
            continue

        first_line = raw.splitlines()[0].strip()
        title = first_line.lstrip("# ").strip() if first_line.startswith("#") else file_path.stem
        words = [w.lower() for w in _TOKEN_PATTERN.findall(raw)]

        # Keep lightweight keyword extraction from file content.
        keyword_counts: dict[str, int] = {}
        for word in words:
            if word in _GENERIC_WORDS:
                continue
            keyword_counts[word] = keyword_counts.get(word, 0) + 1
        keywords = [kw for kw, _ in sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True)[:40]]

        entries.append(
            {
                "id": f"FILE-{file_path.stem}",
                "title": title,
                "keywords": keywords,
                "solution": raw,
                "source": str(file_path.relative_to(Path(__file__).resolve().parent.parent)),
            }
        )

    return entries


LOCAL_KB: list[dict[str, Any]] = _load_folder_kb()


def _search_local_kb(query: str, max_results: int = 3, confidence_threshold: float = 0.4) -> list[dict]:
    words = [w for w in re.sub(r"[^\w\s]", "", query.lower()).split() if len(w) >= 3]
    if not words:
        return []
    scored = []
    for fiche in LOCAL_KB:
        searchable = " ".join([fiche["title"], fiche["solution"], *fiche["keywords"]]).lower()
        word_matches = sum(1 for w in words if w in searchable)
        keyword_hits = sum(
            1 for kw in fiche["keywords"]
            if any(w in kw.lower() or kw.lower() in w for w in words if len(w) >= 3)
        )
        raw_score = word_matches * 0.15 + keyword_hits * 0.4
        if raw_score >= confidence_threshold:
            scored.append({
                "id": fiche["id"],
                "type": "local_kb",
                "title": fiche["title"],
                "solution": fiche["solution"],
                "confidence": round(min(raw_score, 1.0), 2),
                "_raw_score": raw_score,
                "source": fiche["source"],
            })
    scored.sort(key=lambda x: x["_raw_score"], reverse=True)
    for r in scored:
        del r["_raw_score"]
    return scored[:max_results]


SYSTEM_PROMPT = """Tu es un agent de support IT en self-service pour le personnel non-IT du CD08 (Finance, RH, Juridique, Administratif).
Tu DOIS utiliser les outils pour répondre et toujours répondre en français.
Étape 1 : appelle search_knowledge_base pour le problème.
Étape 2a : si action=SOLUTION_FOUND, retourne la solution et termine exactement par :
"Cette réponse vous aide-t-elle ? Sinon, voulez-vous que je crée un ticket pour vous ? (oui/non)"
Étape 2b : si action=NO_SOLUTION_FOUND, ne crée pas immédiatement un ticket. Pose des questions courtes pour collecter les détails manquants.
Avant toute création de ticket, collecte au minimum : titre clair, description du problème, périmètre (poste/application/service), impact, date/heure de début (si connue).
Ensuite, fais un récapitulatif et demande exactement :
"Confirmez-vous la création du ticket avec ces informations ? (oui/non)"
N'appelle create_basic_ticket qu'après confirmation positive explicite.
Si l'utilisateur répond non, demande les corrections, mets à jour le brouillon, puis redemande confirmation.
Étape 3 (urgence uniquement) : si l'utilisateur écrit URGENT, CRITICAL ou EMERGENCY, appelle get_support_contact.
"""


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Recherche le problème utilisateur dans la base de connaissances. "
                "Inclut les fiches IT intégrées et les tickets GLPI résolus/clôturés. "
                "À appeler en premier avant de proposer la création d'un ticket."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question utilisateur ou description du problème.",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 3,
                        "description": "Nombre maximal de résultats à retourner.",
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "default": 0.8,
                        "description": "Score de confiance minimal pour inclure un résultat (0–1). En dessous, retourne found=false.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_basic_ticket",
            "description": (
                "Crée un ticket de support GLPI pour l'utilisateur. "
                "À appeler uniquement après collecte des informations clés et confirmation explicite de l'utilisateur."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Titre court du ticket décrivant le problème.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description complète du problème.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "Priorité du ticket.",
                    },
                },
                "required": ["title", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_support_contact",
            "description": "Retourne le numéro du Help Desk et ses horaires en cas d'urgence réelle.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket_by_id",
            "description": "Récupère les détails complets d'un ticket GLPI, y compris son texte de solution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "ID du ticket GLPI.",
                    },
                },
                "required": ["ticket_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_unfound_query",
            "description": "Journalise une requête sans correspondance KB pour améliorer la base de connaissances.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Requête de recherche n'ayant retourné aucun résultat.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


class KbAgent:
    def __init__(self, llm: OpenRouterClient, glpi: GlpiClient) -> None:
        self.llm = llm
        self.glpi = glpi
        self.tool_handlers: dict[str, Callable[..., Any]] = {
            "search_knowledge_base": self._search_knowledge_base,
            "create_basic_ticket": self._create_basic_ticket,
            "get_support_contact": self._get_support_contact,
            "get_ticket_by_id": self._get_ticket_by_id,
            "log_unfound_query": self._log_unfound_query,
        }

    def run(self, user_message: str) -> str:
        form_submission = self._parse_ticket_form_submission(user_message)
        if form_submission:
            result = self._create_basic_ticket(
                title=form_submission["title"],
                description=form_submission["description"],
                priority=form_submission.get("priority", "medium"),
            )
            tid = result.get("ticket_id")
            ticket_url = result.get("ticket_url")
            if tid and ticket_url:
                return (
                    f"Votre ticket GLPI a été créé : **#{tid}**\n\n"
                    f"[Ouvrir le ticket #{tid}]({ticket_url})\n\n"
                    "Le Help Desk répondra sous 4 heures."
                )
            return "Votre ticket support a été créé. Le Help Desk répondra sous 4 heures."

        if self._is_ticket_creation_declined(user_message):
            return "Compris. Je ne crée pas de ticket."

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
                content = assistant_message.get("content")
                if content:
                    return content
                # Model returned empty content — synthesize from last tool result
                return self._fallback_response(messages)

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                arguments = self._tool_arguments(tool_call)
                result = self._call_tool(name, arguments, user_message)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": name,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        return "L'agent a atteint la limite d'appels outils avant de terminer la demande."

    @staticmethod
    def _assistant_message(response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError(f"LLM returned no choices: {response}")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise RuntimeError(f"LLM returned an invalid message: {response}")
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

    def _call_tool(self, name: str, arguments: dict[str, Any], user_message: str) -> Any:
        if "_argument_error" in arguments:
            return {"error": arguments["_argument_error"], "raw_arguments": arguments.get("_raw")}
        handler = self.tool_handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        if name == "create_basic_ticket" and not self._has_create_ticket_intent(user_message):
            return {"error": "La création d'un ticket exige une confirmation explicite de l'utilisateur: oui/non."}
        try:
            return handler(**arguments)
        except Exception as exc:
            return {"error": str(exc), "tool": name, "arguments": arguments}

    def _fallback_response(self, messages: list[dict[str, Any]]) -> str:
        last_tool = next((m for m in reversed(messages) if m.get("role") == "tool"), None)
        if not last_tool:
            return ""
        try:
            result = json.loads(last_tool.get("content", "{}"))
        except (JSONDecodeError, TypeError):
            return ""
        if result.get("created"):
            tid = result.get("ticket_id")
            ticket_url = result.get("ticket_url")
            if tid and ticket_url:
                return (
                    f"Votre ticket GLPI a été créé : **#{tid}**\n\n"
                    f"[Ouvrir le ticket #{tid}]({ticket_url})\n\n"
                    "Le Help Desk répondra sous 4 heures."
                )
            return "Votre ticket support a été créé. Le Help Desk répondra sous 4 heures."
        if result.get("found") is False:
            return "Je n'ai pas trouvé de réponse correspondante dans la base de connaissances. Voulez-vous que je crée un ticket pour vous ? (oui/non)"
        if result.get("found") and result.get("best_solution"):
            return (
                f"**{result.get('title')}**\n\n{result.get('best_solution', '')}\n\n"
                "Cette réponse vous aide-t-elle ? Sinon, voulez-vous que je crée un ticket pour vous ? (oui/non)"
            )
        return ""

    # ── Tool implementations ──────────────────────────────────────────────────

    def _search_knowledge_base(
        self,
        query: str,
        max_results: int = 3,
        confidence_threshold: float = 0.8,
    ) -> dict[str, Any]:
        results = _search_local_kb(query, max_results, confidence_threshold)

        # GLPI RSQL rejects parenthesised OR groups so we run one query per keyword and deduplicate.
        # Generic words are filtered to avoid false-positive ticket matches.
        sig_words = sorted(
            [
                w for w in re.sub(r"[^\w\s]", "", query.lower()).split()
                if len(w) >= 5 and w not in _GENERIC_WORDS
            ],
            key=len,
            reverse=True,
        )
        search_kws = sig_words[:2] if sig_words else []

        # GLPI ticket search — status.id: 5 = Solved, 6 = Closed
        # Post-filter in Python because some GLPI instances ignore the name= filter.
        seen_ticket_ids: set[Any] = set()
        matched_tickets: list[dict[str, Any]] = []
        for kw in search_kws:
            try:
                for ticket in self.glpi.search_items(
                    itemtype="Ticket",
                    filter=f"status.id=in=(5,6) AND name=like=*{kw}*",
                    limit=max_results * 3,
                ) or []:
                    title = (ticket.get("name") or "").lower()
                    if kw.lower() not in title:
                        continue
                    tid = ticket.get("id")
                    if tid not in seen_ticket_ids:
                        seen_ticket_ids.add(tid)
                        matched_tickets.append(ticket)
            except Exception:
                pass

        for ticket in matched_tickets:
            tid = ticket.get("id")
            results.append({
                "id": f"TKT-{tid}",
                "type": "solved_ticket",
                "title": ticket.get("name"),
                "solution": self._fetch_ticket_solution(tid) if tid else "",
                "confidence": 0.85,
                "source": f"Solved Ticket #{tid}",
            })

        results.sort(key=lambda x: x["confidence"], reverse=True)

        actionable = [r for r in results if r["confidence"] >= confidence_threshold]
        if not actionable:
            return {
                "found": False,
                "action": "NO_SOLUTION_FOUND — call create_basic_ticket now",
                "query": query,
            }
        best = actionable[0]
        return {
            "found": True,
            "action": "SOLUTION_FOUND — return this solution to the user, do NOT create a ticket",
            "best_solution": best.get("solution"),
            "title": best.get("title"),
            "source": best.get("source"),
            "confidence": best.get("confidence"),
            "results": actionable[:max_results],
        }

    def _fetch_ticket_solution(self, ticket_id: int) -> str:
        try:
            timeline = request_json(
                "GET",
                f"{self.glpi.api_root}/Assistance/Ticket/{ticket_id}/Timeline",
                headers=self.glpi._auth_headers(),
            ) or []
            solutions, followups = [], []
            for entry in timeline:
                t = entry.get("type")
                if t == "Solution":
                    solutions.append(entry)
                elif t == "Followup":
                    followups.append(entry)
            candidates = solutions or followups
            if candidates:
                best = max(candidates, key=lambda c: len(c.get("item", {}).get("content") or ""))
                raw = best.get("item", {}).get("content") or ""
                return re.sub(r"<[^>]+>", " ", raw).strip()
        except Exception:
            pass
        return ""

    def _create_basic_ticket(
        self,
        title: str,
        description: str,
        priority: str = "medium",
    ) -> dict[str, Any]:
        priority_map = {"low": 2, "medium": 3, "high": 5}
        fields: dict[str, Any] = {
            "name": title,
            "content": description,
            "type": 1,
            "urgency": priority_map.get(priority, 3),
            "impact": 2,
            "priority": priority_map.get(priority, 3),
        }
        result = self.glpi.create_item("Ticket", fields)
        ticket_id = self._extract_ticket_id(result)
        ticket_url = self._build_ticket_url(ticket_id) if ticket_id else None
        return {
            "created": True,
            "ticket_id": ticket_id,
            "ticket_url": ticket_url,
            "message": f"Ticket #{ticket_id} created. Help Desk will respond within 4 hours." if ticket_id else "Ticket created.",
            "raw_result": result,
        }

    @staticmethod
    def _get_support_contact() -> dict[str, Any]:
        return {
            "phone": "+33 XX XX XX XX",
            "hours": "Lundi–Vendredi 8h–18h",
            "location": "Bâtiment A, rez-de-chaussée",
        }

    def _get_ticket_by_id(self, ticket_id: int) -> dict[str, Any]:
        ticket = self.glpi.get_item(itemtype="Ticket", item_id=ticket_id)
        return {
            "id": ticket.get("id"),
            "title": ticket.get("name"),
            "status": ticket.get("status"),
            "content": ticket.get("content"),
            "solution": self._fetch_ticket_solution(ticket_id),
            "date_solved": ticket.get("date_solve"),
        }

    @staticmethod
    def _log_unfound_query(query: str) -> dict[str, Any]:
        return {
            "logged": True,
            "query": query,
            "action": "Sera revu par le Help Desk.",
        }

    @staticmethod
    def _extract_ticket_id(result: Any) -> int | None:
        if isinstance(result, dict):
            direct = result.get("id")
            if isinstance(direct, int):
                return direct
            if isinstance(direct, str) and direct.isdigit():
                return int(direct)

            # Some GLPI responses return nested structures.
            nested_candidates = [result.get("data"), result.get("item"), result.get("items")]
            for candidate in nested_candidates:
                if isinstance(candidate, dict):
                    nested_id = candidate.get("id")
                    if isinstance(nested_id, int):
                        return nested_id
                    if isinstance(nested_id, str) and nested_id.isdigit():
                        return int(nested_id)
                if isinstance(candidate, list):
                    for entry in candidate:
                        if isinstance(entry, dict):
                            nested_id = entry.get("id")
                            if isinstance(nested_id, int):
                                return nested_id
                            if isinstance(nested_id, str) and nested_id.isdigit():
                                return int(nested_id)
        return None

    def _build_ticket_url(self, ticket_id: int) -> str:
        return f"{self.glpi.settings.glpi_base_url}/front/ticket.form.php?id={ticket_id}"

    @staticmethod
    def _extract_current_user_message(user_message: str) -> str:
        marker = "Current user message:"
        if marker in user_message:
            return user_message.rsplit(marker, 1)[1].strip()
        return user_message.strip()

    @classmethod
    def _has_create_ticket_intent(cls, user_message: str) -> bool:
        current = cls._extract_current_user_message(user_message).lower().strip()
        compact = " ".join(current.split())
        if compact.startswith(_TICKET_FORM_PREFIX.lower()):
            return True
        return any(keyword in compact for keyword in _CREATE_CONFIRM_KEYWORDS)

    @classmethod
    def _is_ticket_creation_declined(cls, user_message: str) -> bool:
        current = cls._extract_current_user_message(user_message).lower().strip()
        compact = " ".join(current.split())
        if compact not in _DECLINE_KEYWORDS:
            return False
        whole = user_message.lower()
        return (
            "create a ticket for you" in whole
            or "would you like me to create a ticket" in whole
            or "do you want me to create a ticket" in whole
            or "crée un ticket pour vous" in whole
            or "créer un ticket pour vous" in whole
            or "voulez-vous que je crée un ticket" in whole
        )

    @classmethod
    def _parse_ticket_form_submission(cls, user_message: str) -> dict[str, str] | None:
        current = cls._extract_current_user_message(user_message)
        if not current.startswith(_TICKET_FORM_PREFIX):
            return None
        raw_json = current[len(_TICKET_FORM_PREFIX) :].strip()
        if not raw_json:
            return None
        try:
            payload = json.loads(raw_json)
        except JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        title = str(payload.get("title", "")).strip()
        description = str(payload.get("description", "")).strip()
        priority = str(payload.get("priority", "medium")).strip().lower()
        if not title or not description:
            return None
        if priority not in {"low", "medium", "high"}:
            priority = "medium"
        return {"title": title, "description": description, "priority": priority}
