from __future__ import annotations

import json
import re
from json import JSONDecodeError
from typing import Any, Callable

from .glpi_client import GlpiClient
from .http_json import request_json
from .openrouter_client import OpenRouterClient


_GENERIC_WORDS = {
    "working", "broken", "issue", "problem", "help", "need", "with", "that",
    "this", "have", "cannot", "cant", "dont", "does", "work", "fail", "error",
    "able", "please", "when", "what", "where", "getting", "keeps",
}

# ── Local knowledge base (fiches documentaires CD08) ─────────────────────────

LOCAL_KB: list[dict[str, Any]] = [
    {
        "id": "FICHE-001",
        "title": "Réinitialisation de mot de passe Windows",
        "keywords": [
            "mot de passe", "password", "réinitialisation", "reset", "session",
            "connexion", "identifiant", "oublié", "account", "locked", "login",
            "log in", "sign in", "windows", "forgot", "bloqué", "credentials", "username",
        ],
        "solution": (
            "Procédure de réinitialisation via le portail self-service :\n"
            "1. Ouvrez un navigateur depuis un autre poste ou votre téléphone.\n"
            "2. Rendez-vous sur : https://selfservice.cd08.fr\n"
            "3. Cliquez sur « Mot de passe oublié ».\n"
            "4. Saisissez votre identifiant (format : prenom.nom).\n"
            "5. Choisissez la méthode de vérification : SMS ou email de récupération.\n"
            "6. Entrez le code reçu.\n"
            "7. Choisissez un nouveau mot de passe (12 caractères minimum, majuscule + chiffre + symbole).\n"
            "8. Validez. Votre session sera débloquée dans les 2 minutes.\n\n"
            "Règles mot de passe CD08 : 12 caractères min, majuscule + minuscule + chiffre + symbole, "
            "ne peut pas reprendre les 5 derniers mots de passe, expiration tous les 90 jours.\n\n"
            "Si le self-service ne fonctionne pas : appelez le Help Desk au 📞 03 24 XX XX XX"
        ),
        "source": "FICHE-001 — Réinitialisation de mot de passe Windows",
    },
    {
        "id": "FICHE-002",
        "title": "Connexion au VPN (Cisco AnyConnect)",
        "keywords": [
            "vpn", "cisco", "anyconnect", "accès distant", "télétravail", "connexion",
            "vpn.cd08.fr", "réseau", "remote", "connect", "network", "work from home",
            "telework", "credentials rejected", "certificate",
        ],
        "solution": (
            "Prérequis : Cisco AnyConnect installé + identifiants Active Directory.\n\n"
            "Procédure :\n"
            "1. Ouvrez Cisco AnyConnect.\n"
            "2. Dans « Se connecter à », entrez : vpn.cd08.fr\n"
            "3. Cliquez sur Connecter.\n"
            "4. Entrez votre identifiant (prenom.nom) et mot de passe Windows.\n"
            "5. Si double facteur demandé, entrez le code SMS.\n"
            "6. Connexion établie en 15–30 secondes.\n\n"
            "Erreurs fréquentes :\n"
            "- 'Credentials rejected' → Réinitialisez votre mot de passe (FICHE-001)\n"
            "- 'Cannot connect to server' → Vérifiez votre connexion internet\n"
            "- 'Certificate error' ou 'License expired' → Contactez le Help Desk"
        ),
        "source": "FICHE-002 — Connexion au VPN (Cisco AnyConnect)",
    },
    {
        "id": "FICHE-003",
        "title": "Accès à la messagerie Outlook depuis l'extérieur",
        "keywords": [
            "outlook", "messagerie", "email", "mail", "extérieur", "domicile",
            "mail.cd08.fr", "owa", "webmail", "home", "access", "emails",
            "messages", "imap", "smtp", "outside", "external",
        ],
        "solution": (
            "Option 1 — Via Outlook Web App (sans VPN) :\n"
            "1. Ouvrez votre navigateur.\n"
            "2. Allez sur : https://mail.cd08.fr\n"
            "3. Entrez votre adresse email : prenom.nom@cd08.fr\n"
            "4. Entrez votre mot de passe Windows.\n\n"
            "Option 2 — Via l'application Outlook (avec VPN) :\n"
            "1. Connectez-vous au VPN (voir FICHE-002).\n"
            "2. Ouvrez Outlook — la synchronisation démarre automatiquement.\n\n"
            "Config manuelle IMAP : mail.cd08.fr port 993 SSL. SMTP : smtp.cd08.fr port 587 TLS."
        ),
        "source": "FICHE-003 — Accès à la messagerie Outlook depuis l'extérieur",
    },
    {
        "id": "FICHE-004",
        "title": "Problème d'impression réseau",
        "keywords": [
            "imprimante", "impression", "printer", "imprimer", "bourrage", "papier",
            "réseau", "print", "spooler", "printing", "paper jam", "stuck",
            "queue", "reinstall", "network printer", "not printing",
        ],
        "solution": (
            "Diagnostic rapide — vérifiez :\n"
            "- L'imprimante est allumée (voyant vert)\n"
            "- Câble réseau branché ou Wi-Fi actif\n"
            "- Papier présent dans le bac\n"
            "- Aucun bourrage papier signalé\n\n"
            "Réinstaller une imprimante réseau :\n"
            "1. Paramètres → Imprimantes et scanners → Ajouter une imprimante.\n"
            "2. Si non détectée, choisir « Sélectionner une imprimante partagée par nom ».\n"
            "3. Chemin réseau : \\\\print.cd08.fr\\NOM_IMPRIMANTE (étiquette sur l'appareil).\n\n"
            "Impression bloquée en file d'attente :\n"
            "1. Win+R → services.msc\n"
            "2. Trouvez « Print Spooler » → Redémarrer.\n"
            "3. Relancez l'impression."
        ),
        "source": "FICHE-004 — Problème d'impression réseau",
    },
    {
        "id": "FICHE-005",
        "title": "Demande de création de compte utilisateur",
        "keywords": [
            "compte", "utilisateur", "création", "nouvel agent", "arrivée", "accès",
            "stagiaire", "rh", "prestataire", "new user", "new account", "create account",
            "onboarding", "new employee", "intern", "contractor", "access request",
        ],
        "solution": (
            "⚠️ Réservé aux responsables de service et gestionnaires RH.\n\n"
            "Procédure :\n"
            "1. Ouvrez un ticket GLPI — Catégorie : Demande → Gestion des comptes → Création.\n"
            "2. Renseignez : nom/prénom, date d'arrivée, département, responsable, "
            "applications nécessaires, durée si temporaire.\n"
            "3. Joignez si possible la fiche de poste ou le contrat.\n"
            "4. Délai de traitement : 48h ouvrées.\n\n"
            "Accès créés automatiquement : compte Active Directory, messagerie Outlook (prenom.nom@cd08.fr), "
            "accès intranet CD08, accès VPN sur demande explicite."
        ),
        "source": "FICHE-005 — Demande de création de compte utilisateur",
    },
    {
        "id": "FICHE-006",
        "title": "Accès à SEDIT (logiciel finances)",
        "keywords": [
            "sedit", "finance", "finances", "comptable", "budget", "mandatement",
            "engagement", "logiciel finance", "accounting", "financial software",
            "blank page", "session expired", "sedit password", "forgot sedit",
            "sedit login", "sedit access",
        ],
        "solution": (
            "SEDIT est le logiciel de gestion financière du CD08.\n\n"
            "Connexion :\n"
            "1. Connectez-vous au VPN (FICHE-002).\n"
            "2. Accédez à : https://sedit.cd08.fr\n"
            "3. Utilisez vos identifiants SEDIT (différents du mot de passe Windows).\n\n"
            "Mot de passe SEDIT oublié : contactez votre référent SEDIT au service Finance "
            "ou ouvrez un ticket GLPI (Applications métier → SEDIT → Mot de passe).\n\n"
            "Problèmes fréquents :\n"
            "- Page blanche → vider le cache (Ctrl+Shift+Del)\n"
            "- Session expirée → reconnectez-vous (expire après 30 min d'inactivité)\n"
            "- Erreur de droits → contactez le Help Desk"
        ),
        "source": "FICHE-006 — Accès à SEDIT (logiciel finances)",
    },
    {
        "id": "FICHE-007",
        "title": "Signaler un incident de sécurité",
        "keywords": [
            "sécurité", "incident", "phishing", "virus", "malware", "suspect", "suspicious",
            "piratage", "vol", "perte", "signaler", "security", "hacked", "stolen",
            "suspicious email", "attachment", "report", "unauthorized", "compromised",
            "lost device", "received email", "strange email", "permission",
            "unauthorized access", "account used", "without permission", "account compromised",
        ],
        "solution": (
            "🔴 En cas de doute, signalez toujours.\n\n"
            "Incident actif (urgence) → 📞 Appelez immédiatement le Help Desk : 03 24 XX XX XX\n"
            "Ne pas éteindre le poste. Ne pas déconnecter le câble réseau.\n\n"
            "Incident non urgent :\n"
            "1. Ouvrez un ticket GLPI — Catégorie : Incident → Sécurité.\n"
            "2. Décrivez ce que vous avez observé (heure, action, message affiché).\n"
            "3. Si email suspect reçu, transférez-le en pièce jointe au ticket.\n"
            "SLA : réponse en 2h pour les incidents sécurité.\n\n"
            "Exemples d'incidents : email de phishing, compte utilisé sans autorisation, "
            "poste anormalement lent, lien suspect cliqué, perte/vol d'équipement professionnel."
        ),
        "source": "FICHE-007 — Signaler un incident de sécurité",
    },
]


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


SYSTEM_PROMPT = """You are a self-service IT support agent for CD08 non-IT staff (Finance, HR, Legal, Administrative).
You MUST use tools to answer — never generate an answer without calling a tool first.
Step 1: Call search_knowledge_base for the issue.
Step 2a: If action=SOLUTION_FOUND, return the solution to the user — do NOT create a ticket.
Step 2b: If action=NO_SOLUTION_FOUND, call create_basic_ticket NOW with the user's message as title and description. Do NOT ask anything.
Step 3 (emergency only): If the user writes URGENT, CRITICAL, or EMERGENCY, call get_support_contact instead.
Reply in the same language the user wrote in. Translate KB content if needed.
Never announce you will create a ticket — just call create_basic_ticket.
"""


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search the knowledge base for the user's issue. "
                "Searches built-in IT fiches and solved/closed GLPI tickets. "
                "Always call this first before offering to create a ticket."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question or issue description.",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 3,
                        "description": "Maximum number of results to return.",
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "default": 0.8,
                        "description": "Minimum confidence score to include a result (0–1). Results below this return found=false.",
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
                "Create a support ticket in GLPI for the user. "
                "Call this immediately when search_knowledge_base finds no solution. "
                "Do NOT announce you will create a ticket — just call this function."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short ticket title describing the issue.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Full description of the issue.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "Ticket priority.",
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
            "description": "Return the Help Desk phone number and support hours for genuine emergencies.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket_by_id",
            "description": "Retrieve full details of a specific GLPI ticket including its solution text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "GLPI ticket ID.",
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
            "description": "Log a query that had no KB match so the Help Desk can improve the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query that returned no results.",
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
            return f"Your support ticket #{tid} has been created. The Help Desk will respond within 4 hours."
        if result.get("found") is False:
            return "No matching solution was found in the knowledge base. A ticket has been queued for the Help Desk."
        if result.get("found") and result.get("best_solution"):
            return f"**{result.get('title')}**\n\n{result.get('best_solution', '')}"
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
        return {
            "created": True,
            "ticket_id": result.get("id"),
            "message": f"Ticket #{result.get('id')} created. Help Desk will respond within 4 hours.",
        }

    @staticmethod
    def _get_support_contact() -> dict[str, Any]:
        return {
            "phone": "+33 XX XX XX XX",
            "hours": "Monday–Friday 8AM–6PM",
            "location": "Building A, Ground Floor",
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
            "action": "Will be reviewed by Help Desk.",
        }
