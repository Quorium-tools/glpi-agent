"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
};

const starterPrompts = [
  "How do I reset my password?",
  "How do I connect to the VPN?",
  "My printer is not working.",
  "I received a suspicious email.",
  "How do I access SEDIT?",
  "How do I request an account for a new employee?",
];

export default function DepartmentsSupportAgentPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm the self-service IT support assistant for CD08. Ask me about passwords, VPN, printers, email, SEDIT, or report a security incident. I'll answer directly or open a ticket for you.",
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
    if (!prompt || isSending) {
      return;
    }

    setInput("");
    setIsSending(true);
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: prompt,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent: "departments-support-agent",
          message: prompt,
          model: model.trim() || undefined,
        }),
      });
      const data = await response.json();
      const answer = response.ok ? data.answer : `${data.error}\n${data.detail || ""}`.trim();

      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: answer,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: error instanceof Error ? error.message : "The request failed.",
        },
      ]);
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(input);
  }

  function handlePromptClick(prompt: string) {
    setInput(prompt);
    inputRef.current?.focus();
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-mark">DS</div>
          <h1>Departments Support Agent</h1>
          <p>Self-service IT support for Finance, HR, Legal, and other non-IT departments.</p>
        </div>

        <div className="prompt-list">
          <span>Try</span>
          {starterPrompts.map((prompt) => (
            <button key={prompt} type="button" onClick={() => handlePromptClick(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <div style={{ marginTop: "auto", paddingTop: "1rem", fontSize: "0.8rem", opacity: 0.6 }}>
          <Link href="/help-desk-agent">Switch to IT Admin Agent</Link>
        </div>
      </aside>

      <section className="chat-panel">
        <header className="chat-header">
          <div>
            <strong>Departments Support Agent — Self-service</strong>
            <span>Describe your issue and I'll help or open a ticket</span>
          </div>
          <div className={`status-pill ${isSending ? "busy" : ""}`}>
            <span />
            {isSending ? "Working" : "Ready"}
          </div>
        </header>

        <div className="messages">
          {messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                <span>{message.role === "assistant" ? "AI" : "ME"}</span>
              </div>
              <div className="message-bubble">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            </article>
          ))}
          {isSending && (
            <article className="message assistant">
              <div className="message-avatar">
                <span>AI</span>
              </div>
              <div className="message-bubble typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void sendMessage(input);
              }
            }}
            placeholder="Ask: how do I reset my password?"
            rows={2}
          />
          <button type="submit" disabled={!canSend}>
            Send
          </button>
        </form>
      </section>
    </main>
  );
}
