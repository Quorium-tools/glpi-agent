"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
};

const starterPrompts = [
  "List all tickets I have.",
  "Suggest a solution for ticket 1.",
  "Create a ticket task for ticket 1: checked printer queue, duration 15 minutes.",
  "Generate a ticket report grouped by status and priority.",
  "Search printers with name like accounting.",
];

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi. Ask me to create, list, read, update, delete, or solve tickets. I can also suggest support solutions before saving them.",
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
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: prompt,
          messages: nextMessages.slice(-8).map(({ role, content }) => ({ role, content })),
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

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-mark">G</div>
          <h1>GLPI Agent</h1>
          <p>OpenRouter-powered assistant connected to your GLPI API V2 tools.</p>
        </div>

        <div className="settings-panel">
          <label className="field-label">
            Model override
            <input
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder="openai/gpt-4o-mini"
            />
          </label>
        </div>

        <div className="prompt-list">
          <span>Try</span>
          {starterPrompts.map((prompt) => (
            <button key={prompt} type="button" onClick={() => void sendMessage(prompt)}>
              {prompt}
            </button>
          ))}
        </div>
      </aside>

      <section className="chat-panel">
        <header className="chat-header">
          <div>
            <strong>Agent Chat</strong>
            <span>Live GLPI writes enabled</span>
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
                {message.content.split("\n").map((line, index) => (
                  <p key={`${message.id}-${index}`}>{line || "\u00a0"}</p>
                ))}
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
            placeholder="Ask: can u list all tickets i have"
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
