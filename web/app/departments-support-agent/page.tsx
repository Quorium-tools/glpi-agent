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

type TicketDraft = {
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "very high" | "major";
};

const DECISION_FEEDBACK_WORDS = new Set(["no","n","yes","y","not helpful","not helpful!","not useful","create ticket"]);

function isTicketDecisionPrompt(text: string): boolean {
  const n = text.toLowerCase();
  return (
    /create a ticket for you\?\s*\((yes\/no|y\/n)\)/.test(n) ||
    /would you like me to create a ticket/.test(n) ||
    /do you want me to create a ticket/.test(n)
  );
}

function looksLikeDecisionFeedback(text: string): boolean {
  return DECISION_FEEDBACK_WORDS.has(text.toLowerCase().trim());
}

function buildTicketDraft(issue: string, previousGuidance: string): TicketDraft {
  const normalizedIssue = issue.trim() || "Support request";
  let subject = "IT support";
  const lower = normalizedIssue.toLowerCase();
  if (lower.includes("printer") || lower.includes("print")) subject = "Printer";
  else if (lower.includes("password")) subject = "Password";
  else if (lower.includes("vpn")) subject = "VPN";
  else if (lower.includes("email") || lower.includes("outlook")) subject = "Email";
  else if (lower.includes("sedit")) subject = "SEDIT";
  else if (lower.includes("security") || lower.includes("phishing")) subject = "Security";

  const title = `${subject} issue: ${normalizedIssue.slice(0, 90)}`.trim();
  const compactGuidance = previousGuidance
    .replace(/\s+/g, " ")
    .replace(/is this answer helpful\?.*/i, "")
    .replace(/would you like me to create a ticket.*$/i, "")
    .trim();

  const description = [
    `User issue: ${normalizedIssue}`,
    "",
    "Observed behavior:",
    "- The issue is still unresolved after self-service guidance.",
    "",
    "Troubleshooting already attempted:",
    compactGuidance ? `- ${compactGuidance.slice(0, 500)}` : "- Initial troubleshooting attempted; issue persists.",
    "",
    "Business impact:",
    "- User cannot complete normal work due to this issue.",
  ].join("\n");

  return { title: title.slice(0, 120), description, priority: "medium" };
}

const starterPrompts = [
  "How do I reset my password?",
  "How do I connect to the VPN?",
  "My printer is not working.",
  "I received a suspicious email.",
  "How do I access SEDIT?",
  "How do I request an account for a new employee?",
];

const DEFAULT_OPENROUTER_MODEL = "anthropic/claude-opus-4.7";
const OPENROUTER_MODEL_BADGE =
  process.env.NEXT_PUBLIC_OPENROUTER_MODEL?.trim() || DEFAULT_OPENROUTER_MODEL;

function TicketFormCard({
  draft,
  isSending,
  onChange,
  onSubmit,
  onDiscard,
}: {
  draft: TicketDraft;
  isSending: boolean;
  onChange: (d: TicketDraft) => void;
  onSubmit: () => void;
  onDiscard: () => void;
}) {
  const [collapsing, setCollapsing] = useState(false);

  function handleSubmit() {
    setCollapsing(true);
    setTimeout(onSubmit, 380);
  }

  function handleDiscard() {
    setCollapsing(true);
    setTimeout(onDiscard, 380);
  }

  return (
    <div className={`ticket-card${collapsing ? " ticket-card--collapsing" : ""}`}>
      <div className="ticket-card-header">
        <div className="ticket-card-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/>
            <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            <line x1="12" y1="12" x2="12" y2="16"/>
            <line x1="10" y1="14" x2="14" y2="14"/>
          </svg>
        </div>
        <div>
          <strong>Create Ticket</strong>
          <span>Review and submit to Help Desk</span>
        </div>
        <button type="button" className="ticket-card-discard" onClick={handleDiscard} title="Discard">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div className="ticket-card-fields">
        <div className="ticket-card-field">
          <label>Title</label>
          <input
            value={draft.title}
            onChange={(e) => onChange({ ...draft, title: e.target.value })}
            placeholder="Ticket title"
          />
        </div>
        <div className="ticket-card-field">
          <label>Description</label>
          <textarea
            value={draft.description}
            onChange={(e) => onChange({ ...draft, description: e.target.value })}
            placeholder="Describe your issue"
            rows={4}
          />
        </div>
        <div className="ticket-card-field ticket-card-field--row">
          <div className="ticket-card-field" style={{ flex: 1 }}>
            <label>Priority</label>
            <div className="priority-pills">
              {(["low", "medium", "high", "very high", "major"] as const).map((p) => (
                <button
                  key={p}
                  type="button"
                  className={`priority-pill priority-pill--${p.replace(" ", "-")}${draft.priority === p ? " priority-pill--active" : ""}`}
                  onClick={() => onChange({ ...draft, priority: p })}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            className="ticket-card-submit"
            onClick={handleSubmit}
            disabled={isSending || !draft.title.trim() || !draft.description.trim() || collapsing}
          >
            {isSending ? (
              <svg className="status-spinner" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="20 14" />
              </svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            )}
            Submit Ticket
          </button>
        </div>
      </div>
    </div>
  );
}

export default function DepartmentsSupportAgentPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi! I'm the self-service IT support assistant for CD08. Ask me about passwords, VPN, printers, email, SEDIT, or report a security incident. I'll answer directly or open a ticket for you.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [pendingTicketDraft, setPendingTicketDraft] = useState<TicketDraft | null>(null);
  const [awaitingTicketDecision, setAwaitingTicketDecision] = useState(false);
  const [lastIssueForTicket, setLastIssueForTicket] = useState("");
  const [lastGuidanceForTicket, setLastGuidanceForTicket] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const canSend = useMemo(() => input.trim().length > 0 && !isSending, [input, isSending]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isSending, pendingTicketDraft]);

  async function sendMessage(text: string) {
    const prompt = text.trim();
    if (!prompt || isSending) return;

    const lowerPrompt = prompt.toLowerCase();

    if (awaitingTicketDecision && (lowerPrompt === "yes" || lowerPrompt === "y" || lowerPrompt.includes("create ticket"))) {
      setInput("");
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "user", content: prompt }]);
      setPendingTicketDraft(buildTicketDraft(lastIssueForTicket, lastGuidanceForTicket));
      setAwaitingTicketDecision(false);
      return;
    }

    if (awaitingTicketDecision && (lowerPrompt === "no" || lowerPrompt === "n")) {
      setInput("");
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "user", content: prompt }]);
      setAwaitingTicketDecision(false);
      setPendingTicketDraft(null);
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: "Understood. I will not create a ticket." }]);
      return;
    }

    setInput("");
    setIsSending(true);
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: prompt };
    if (!looksLikeDecisionFeedback(prompt)) setLastIssueForTicket(prompt);
    setMessages((c) => [...c, userMessage]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: "departments-support-agent",
          message: prompt,
          messages: [...messages, userMessage].slice(-8).map(({ role, content }) => ({ role, content })),
        }),
      });
      const data = await response.json();
      const answer = response.ok ? data.answer : `${data.error}\n${data.detail || ""}`.trim();
      const asksTicketCreation = isTicketDecisionPrompt(answer);
      if (asksTicketCreation) setLastGuidanceForTicket(answer);
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: answer }]);
      setAwaitingTicketDecision(asksTicketCreation);
    } catch (error) {
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: error instanceof Error ? error.message : "The request failed." }]);
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  }

  async function submitTicketDraft() {
    if (!pendingTicketDraft || isSending) return;
    setIsSending(true);
    setMessages((c) => [...c, { id: crypto.randomUUID(), role: "user", content: `Create ticket: ${pendingTicketDraft.title}` }]);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: "departments-support-agent",
          message: `__TICKET_FORM__ ${JSON.stringify(pendingTicketDraft)}`,
          messages: messages.slice(-8).map(({ role, content }) => ({ role, content })),
        }),
      });
      const data = await response.json();
      const answer = response.ok ? data.answer : `${data.error}\n${data.detail || ""}`.trim();
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: answer }]);
      setPendingTicketDraft(null);
      setAwaitingTicketDecision(false);
    } catch (error) {
      setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: error instanceof Error ? error.message : "The request failed." }]);
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
    <main className="app-shell theme-ds">

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
          <Link href="/help-desk-agent" className="agent-switcher-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            Help Desk Agent
          </Link>
          <span className="agent-switcher-pill active">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2"/>
              <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            </svg>
            Departments Support Agent
          </span>
        </div>
      </nav>

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-identity">
            <div className="brand-mark">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
                <line x1="12" y1="12" x2="12" y2="16"/>
                <line x1="10" y1="14" x2="14" y2="14"/>
              </svg>
            </div>
            <div>
              <h1>Departments Support</h1>
              <p>Self-service IT support for Finance, HR, Legal, and other departments.</p>
            </div>
          </div>
        </div>

        <div className="prompt-list">
          <span>Try asking</span>
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
            <strong>Departments Support Agent</strong>
            <span>Describe your issue — I'll help or open a ticket</span>
          </div>
          <div className={`status-pill ${isSending ? "busy" : ""}`}>
            {isSending ? (
              <svg className="status-spinner" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="20 14" />
              </svg>
            ) : (
              <span />
            )}
            {isSending ? "Working…" : "Ready"}
          </div>
        </header>

        <div className="messages">
          {messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                <span>{message.role === "assistant" ? "DS" : "ME"}</span>
              </div>
              <div className="message-bubble">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ a: ({ ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" /> }}>{message.content}</ReactMarkdown>
              </div>
            </article>
          ))}
          {pendingTicketDraft && (
            <article className="message assistant ticket-card-message">
              <div className="message-avatar"><span>DS</span></div>
              <TicketFormCard
                draft={pendingTicketDraft}
                isSending={isSending}
                onChange={(d) => setPendingTicketDraft(d)}
                onSubmit={() => void submitTicketDraft()}
                onDiscard={() => {
                  setPendingTicketDraft(null);
                  setAwaitingTicketDecision(false);
                  setMessages((c) => [...c, { id: crypto.randomUUID(), role: "assistant", content: "Ticket discarded. Let me know if you need anything else." }]);
                }}
              />
            </article>
          )}
          {isSending && (
            <article className="message assistant">
              <div className="message-avatar"><span>DS</span></div>
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
            placeholder="Ask: how do I reset my password?"
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
