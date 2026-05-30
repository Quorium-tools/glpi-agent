"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
};

type ParsedTicketLine = {
  id: number;
  title: string;
  status: string;
  priorityCode: number | null;
  priorityLabel: string;
};

const starterPrompts = [
  "Liste tous mes tickets.",
  "Propose une solution pour le ticket 1.",
  "Crée une tâche sur le ticket 1 : vérification de la file d'impression, durée 15 minutes.",
  "Génère un rapport de tickets groupé par statut et priorité.",
  "Recherche les imprimantes dont le nom contient compta.",
];

const PRIORITY_LABEL_BY_CODE: Record<number, string> = {
  1: "Très faible",
  2: "Faible",
  3: "Moyenne",
  4: "Haute",
  5: "Très haute",
  6: "Majeure",
};

const DEFAULT_OPENROUTER_MODEL = "anthropic/claude-opus-4.7";
const OPENROUTER_MODEL_BADGE =
  process.env.NEXT_PUBLIC_OPENROUTER_MODEL?.trim() || DEFAULT_OPENROUTER_MODEL;

function parseTicketListMessage(content: string): {
  intro: string | null;
  tickets: ParsedTicketLine[];
  outro: string | null;
} | null {
  const lines = content
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const tickets: ParsedTicketLine[] = [];

  for (const rawLine of lines) {
    const line = rawLine.replace(/^"+|"+$/g, "");
    const match = line.match(/^#?(\d+)\s*-\s*(.*?)\s*\|\s*([^|]+)\s*\|\s*(.+)$/i);
    if (!match) continue;
    const [, idText, title, status, priorityRaw] = match;
    const codeMatch = priorityRaw.match(/\bP?([1-6])\b/i) || priorityRaw.match(/\(([1-6])\)/);
    const priorityCode = codeMatch ? Number(codeMatch[1]) : null;
    const priorityLabel = priorityCode ? PRIORITY_LABEL_BY_CODE[priorityCode] : priorityRaw.trim();
    tickets.push({ id: Number(idText), title: title.trim(), status: status.trim(), priorityCode, priorityLabel });
  }

  if (!tickets.length) return null;

  const firstTicketIndex = lines.findIndex((line) => /^"?#?\d+\s*-/.test(line));
  const lastTicketIndex = lines.length - 1 - [...lines].reverse().findIndex((line) => /^"?#?\d+\s*-/.test(line));
  const intro = firstTicketIndex > 0 ? lines.slice(0, firstTicketIndex).join(" ") : null;
  const outro = lastTicketIndex < lines.length - 1 ? lines.slice(lastTicketIndex + 1).join(" ") : null;

  return { intro, tickets, outro };
}

export default function HelpDeskAgentPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Bonjour. Je peux créer, lister, lire, mettre à jour, supprimer ou résoudre des tickets. Je peux aussi proposer des solutions avant enregistrement.",
    },
  ]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState("");
  const [isSending, setIsSending] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const canSend = useMemo(() => input.trim().length > 0 && !isSending, [input, isSending]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isSending]);

  async function sendMessage(text: string) {
    const prompt = text.trim();
    if (!prompt || isSending) return;
    setInput("");
    setIsSending(true);
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: prompt };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: "admin",
          message: prompt,
          messages: nextMessages.slice(-8).map(({ role, content }) => ({ role, content })),
          model: model.trim() || undefined,
        }),
      });
      const data = await response.json();
      const answer = response.ok ? data.answer : `${data.error}\n${data.detail || ""}`.trim();
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: answer }]);
    } catch (error) {
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: error instanceof Error ? error.message : "La requête a échoué." }]);
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    void sendMessage(input);
  }

  return (
    <main className="app-shell theme-hd">

      {/* Full-width top navbar */}
      <nav className="app-navbar">
        <div className="navbar-left">
          <Link href="/" className="sidebar-navbar-logos">
            <Image src="/ardennes_logo.png" alt="Ardennes" width={100} height={28} style={{ alignSelf: "center", transform: "translateY(-4px)" }} />
            <span className="sidebar-navbar-sep">×</span>
            <Image src="/glpi_logo.png" alt="GLPI" width={50} height={31} style={{ alignSelf: "center" }} />
          </Link>
          <div className="navbar-divider" aria-hidden />
          <div className="navbar-model-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
              <circle cx="9" cy="14" r="1" fill="currentColor" stroke="none"/>
              <circle cx="15" cy="14" r="1" fill="currentColor" stroke="none"/>
            </svg>
            <span>{OPENROUTER_MODEL_BADGE}</span>
          </div>
        </div>
        <div className="agent-switcher">
          <span className="agent-switcher-pill active">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            Agent Help Desk
          </span>
          <Link href="/departments-support-agent" className="agent-switcher-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2"/>
              <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            </svg>
            Agent Support Départements
          </Link>
        </div>
      </nav>

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-top">
          {/* Identity */}
          <div className="sidebar-identity">
            <div className="brand-mark">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <div>
              <h1>Agent Help Desk</h1>
              <p>Assistant propulsé par OpenRouter, connecté à vos outils GLPI API V2.</p>
            </div>
          </div>
        </div>

        {/* Prompts */}
        <div className="prompt-list">
          <span>Exemples de demandes</span>
          {starterPrompts.map((prompt) => (
            <button key={prompt} type="button" onClick={() => { setInput(prompt); inputRef.current?.focus(); }}>
              {prompt}
            </button>
          ))}
        </div>
      </aside>

      {/* Chat */}
      <section className="chat-panel">
        <header className="chat-header">
          <div>
            <strong>Agent Help Desk</strong>
            <span>Écriture GLPI active</span>
          </div>
          <div className={`status-pill ${isSending ? "busy" : ""}`}>
            {isSending ? (
              <svg className="status-spinner" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="20 14" />
              </svg>
            ) : (
              <span />
            )}
            {isSending ? "Traitement…" : "Prêt"}
          </div>
        </header>

        <div className="messages">
          {messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                <span>{message.role === "assistant" ? "HD" : "MOI"}</span>
              </div>
              <div className="message-bubble">
                {message.role === "assistant" && parseTicketListMessage(message.content) ? (
                  (() => {
                    const parsed = parseTicketListMessage(message.content)!;
                    return (
                      <div className="ticket-list-block">
                        {parsed.intro && <p>{parsed.intro}</p>}
                        <div className="ticket-cards">
                          {parsed.tickets.map((ticket) => (
                            <article key={ticket.id} className="ticket-card">
                              <div className="ticket-card-top">
                                <strong>#{ticket.id}</strong>
                                <p>{ticket.title}</p>
                                <span className={`ticket-status ${ticket.status.toLowerCase().includes("closed") ? "closed" : ticket.status.toLowerCase().includes("solved") ? "solved" : "open"}`}>
                                  {ticket.status}
                                </span>
                                <span className="ticket-priority">
                                  <span className={`ticket-priority-badge ${ticket.priorityCode && ticket.priorityCode >= 5 ? "critical" : ticket.priorityCode === 4 ? "high" : ticket.priorityCode === 3 ? "medium" : "low"}`}>
                                    {ticket.priorityLabel}
                                  </span>
                                </span>
                              </div>
                            </article>
                          ))}
                        </div>
                        {parsed.outro && <p>{parsed.outro}</p>}
                      </div>
                    );
                  })()
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                )}
              </div>
            </article>
          ))}
          {isSending && (
            <article className="message assistant">
              <div className="message-avatar"><span>HD</span></div>
              <div className="message-bubble typing"><span /><span /><span /></div>
            </article>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void sendMessage(input); } }}
            placeholder="Demandez des tickets, utilisateurs ou assets…"
            rows={1}
          />
          <button type="submit" disabled={!canSend}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </section>
    </main>
  );
}
